#!/usr/bin/env python3
"""Run every Tool Finder provider that is available and report skipped providers."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from export_tool_report import filter_payload_by_scope, write_report_bundle, write_tools_markdown
from tool_finder_common import dump_json, final_rank_results, provider_status, score_result


SCRIPT_DIR = Path(__file__).resolve().parent
REGISTRY_SOURCES = {"npm", "python", "pypi", "pips", "homebrew"}
REGISTRY_SOURCE_PREFERENCE = {
    "homebrew": 5,
    "npm": 4,
    "python": 3,
    "pypi": 2,
    "pips": 2,
}


def normalize_alias_value(value: str) -> str:
    name = str(value or "").strip().lower()
    if name.startswith("@") and "/" in name:
        name = name.split("/", 1)[1]
    return "".join(char for char in name if char.isalnum() or char in {"-", "_", "."})


def add_alias_group(alias_map: dict[str, str], canonical: str, aliases: list[str]) -> None:
    canonical_key = normalize_alias_value(canonical)
    if not canonical_key:
        return
    alias_map[canonical_key] = canonical_key
    for alias in aliases:
        alias_key = normalize_alias_value(alias)
        if alias_key:
            alias_map[alias_key] = canonical_key


def load_alias_file(path: str) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    raw_aliases = payload.get("aliases") if isinstance(payload, dict) else payload
    if isinstance(raw_aliases, dict):
        for canonical, aliases in raw_aliases.items():
            if isinstance(aliases, str):
                alias_values = [aliases]
            elif isinstance(aliases, list):
                alias_values = [str(alias) for alias in aliases]
            else:
                alias_values = []
            add_alias_group(alias_map, str(canonical), alias_values)
    elif isinstance(raw_aliases, list):
        for group in raw_aliases:
            if not isinstance(group, dict):
                continue
            canonical = str(group.get("canonical") or "")
            aliases = [str(alias) for alias in group.get("aliases") or []]
            add_alias_group(alias_map, canonical, aliases)
    return alias_map


def parse_inline_alias(value: str) -> tuple[str, list[str]]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected canonical=alias1,alias2.")
    canonical, aliases = value.split("=", 1)
    alias_values = [alias.strip() for alias in aliases.split(",") if alias.strip()]
    if not canonical.strip() or not alias_values:
        raise argparse.ArgumentTypeError("Expected canonical=alias1,alias2.")
    return canonical.strip(), alias_values


def load_dedupe_aliases(paths: list[str], inline_aliases: list[tuple[str, list[str]]]) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for path in paths:
        alias_map.update(load_alias_file(path))
    for canonical, aliases in inline_aliases:
        add_alias_group(alias_map, canonical, aliases)
    return alias_map


def parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def run_json(command: list[str], *, timeout: int = 60, env: dict[str, str] | None = None) -> tuple[dict[str, Any] | None, str | None]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except FileNotFoundError as error:
        return None, f"Command not found: {error.filename}"
    except subprocess.TimeoutExpired:
        return None, f"Command timed out after {timeout} seconds."

    output = completed.stdout.strip()
    error_output = completed.stderr.strip()
    if completed.returncode != 0:
        detail = error_output or output or f"Exited with status {completed.returncode}."
        try:
            parsed = parse_json(output or error_output)
            detail = parsed.get("error") or parsed.get("reason") or detail
        except Exception:
            pass
        return None, detail

    try:
        payload = parse_json(output)
    except Exception as error:
        return None, f"Could not parse JSON output: {error}"
    if not isinstance(payload, dict):
        return None, "Provider returned JSON that was not an object."
    return payload, None


def provider_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("results"), list):
        return payload["results"]
    if isinstance(payload.get("result"), dict):
        return [payload["result"]]
    return []


def statuses_from_payload(
    payload: dict[str, Any],
    *,
    provider: str,
    variant: str | None = None,
    default_state: str = "queried",
) -> list[dict[str, Any]]:
    payload_status = payload.get("providerStatus")
    if isinstance(payload_status, list) and payload_status:
        return payload_status
    if isinstance(payload_status, dict):
        return [payload_status]
    count = len(provider_results(payload))
    return [
        provider_status(
            provider,
            variant=variant,
            state=default_state,
            searched=True,
            reason=f"{provider} provider completed.",
            result_count=count,
        )
    ]


def error_status(provider: str, reason: str, *, variant: str | None = None) -> dict[str, Any]:
    return provider_status(
        provider,
        variant=variant,
        state="error",
        searched=True,
        skipped=True,
        reason=reason,
        remediation=["Check network access, provider auth, and the provider helper script."],
        result_count=0,
    )


def skipped_status(
    provider: str,
    reason: str,
    *,
    variant: str | None = None,
    requires_auth: bool = False,
    remediation: list[str] | None = None,
) -> dict[str, Any]:
    return provider_status(
        provider,
        variant=variant,
        state="skipped",
        searched=False,
        skipped=True,
        requires_auth=requires_auth,
        reason=reason,
        remediation=remediation or [],
        result_count=0,
    )


def attach_status(results: list[dict[str, Any]], status: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    enriched_status = {**status, "resultCount": len(results)}
    for result in results:
        copy = dict(result)
        existing_status = dict(copy.get("providerStatus") or {})
        item_status = {**enriched_status, **existing_status}
        if not existing_status.get("provider"):
            item_status["provider"] = enriched_status.get("provider")
        if not existing_status.get("variant"):
            item_status["variant"] = enriched_status.get("variant")
        if item_status.get("resultCount") is None:
            item_status["resultCount"] = len(results)
        copy["providerStatus"] = item_status
        out.append(score_result(copy))
    return out


def read_gh_auth_token() -> str | None:
    gh_path = shutil.which("gh")
    if not gh_path:
        return None
    try:
        completed = subprocess.run(
            [gh_path, "auth", "token"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return None
    token = completed.stdout.strip()
    if completed.returncode != 0 or not token:
        return None
    return token


def registry_name_candidates(item: dict[str, Any]) -> list[str]:
    external_ids = item.get("externalIds") or {}
    location = item.get("location") or {}
    candidates = [
        item.get("name"),
        location.get("path"),
        external_ids.get("npmName"),
        external_ids.get("pypiName"),
        external_ids.get("homebrewName"),
        external_ids.get("homebrewToken"),
    ]
    out: list[str] = []
    for candidate in candidates:
        normalized = normalize_alias_value(str(candidate or ""))
        if normalized and normalized not in out:
            out.append(normalized)
    return out


def canonical_registry_name(item: dict[str, Any], aliases: dict[str, str]) -> str | None:
    if item.get("source") not in REGISTRY_SOURCES:
        return None
    candidates = registry_name_candidates(item)
    for candidate in candidates:
        if candidate in aliases:
            return aliases[candidate]
    return candidates[0] if candidates else None


def provider_variant(item: dict[str, Any]) -> dict[str, Any]:
    install = item.get("install") or {}
    location = item.get("location") or {}
    provider = item.get("providerStatus") or {}
    return {
        "name": item.get("name"),
        "source": item.get("source"),
        "provider": provider.get("provider") or item.get("source"),
        "variant": provider.get("variant"),
        "state": provider.get("state"),
        "score": item.get("score", 0),
        "install": install.get("command") or install.get("installUrl") or install.get("status"),
        "url": location.get("url") or install.get("installUrl"),
    }


def better_registry_result(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_key = (int(a.get("score") or 0), REGISTRY_SOURCE_PREFERENCE.get(str(a.get("source")), 0))
    b_key = (int(b.get("score") or 0), REGISTRY_SOURCE_PREFERENCE.get(str(b.get("source")), 0))
    return a if a_key >= b_key else b


def merge_registry_duplicate(primary: dict[str, Any], duplicate: dict[str, Any]) -> dict[str, Any]:
    variants = list(primary.get("providerVariants") or [provider_variant(primary)])
    variants.extend(duplicate.get("providerVariants") or [provider_variant(duplicate)])
    primary["providerVariants"] = variants
    primary["alternatives"] = list(primary.get("alternatives") or []) + [{
        "name": duplicate.get("name"),
        "source": duplicate.get("source"),
        "whyConsider": f"Also returned by {duplicate.get('source')} for the same registry candidate name.",
        "score": duplicate.get("score", 0),
        "install": (duplicate.get("install") or {}).get("command") or (duplicate.get("install") or {}).get("installUrl"),
    }]
    primary["reasons"] = list(primary.get("reasons") or [])
    merge_note = "Registry duplicate merged; see providerVariants for alternate package-manager hits."
    if merge_note not in primary["reasons"]:
        primary["reasons"].append(merge_note)
    provider = dict(primary.get("providerStatus") or {})
    provider["additionalProviders"] = [
        {
            "provider": variant.get("provider"),
            "variant": variant.get("variant"),
            "source": variant.get("source"),
            "state": variant.get("state"),
        }
        for variant in variants
    ]
    primary["providerStatus"] = provider
    return primary


def dedupe_registry_results(results: list[dict[str, Any]], aliases: dict[str, str]) -> tuple[list[dict[str, Any]], int]:
    grouped: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    duplicate_count = 0
    passthrough: list[dict[str, Any]] = []

    for item in results:
        key = canonical_registry_name(item, aliases)
        if not key:
            passthrough.append(item)
            continue
        if key not in grouped:
            grouped[key] = item
            order.append(key)
            continue

        duplicate_count += 1
        existing = grouped[key]
        preferred = better_registry_result(existing, item)
        duplicate = item if preferred is existing else existing
        grouped[key] = merge_registry_duplicate(preferred, duplicate)

    return passthrough + [grouped[key] for key in order], duplicate_count


def run_provider(
    provider: str,
    command: list[str],
    *,
    variant: str | None = None,
    timeout: int = 60,
    env: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
    payload, error = run_json(command, timeout=timeout, env=env)
    if error:
        status = error_status(provider, error, variant=variant)
        return [], [status], None
    assert payload is not None
    statuses = statuses_from_payload(payload, provider=provider, variant=variant)
    results = provider_results(payload)
    status_for_results = statuses[0] if statuses else provider_status(provider, state="queried", searched=True)
    return attach_status(results, status_for_results), statuses, payload


def run_all(
    query: str,
    *,
    roots: list[str],
    limit: int,
    local_limit: int,
    runtime_catalog: str | None,
    github_token_env: str,
    include_github_code: bool,
    use_gh_token: bool,
    dedupe_aliases: dict[str, str],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    provider_payloads: dict[str, Any] = {}

    if runtime_catalog:
        runtime_results, runtime_statuses, payload = run_provider(
            "runtime",
            [sys.executable, str(SCRIPT_DIR / "search_runtime_tools.py"), runtime_catalog],
            variant="catalog",
        )
        results.extend(runtime_results)
        statuses.extend(runtime_statuses)
        provider_payloads["runtime"] = payload
    else:
        statuses.append(skipped_status(
            "runtime",
            "No runtime catalog JSON was supplied to the all-provider command.",
            variant="catalog",
            remediation=["Pass --runtime-catalog with a live Codex tool catalog JSON file when running outside an assistant turn."],
        ))

    if local_limit > 0:
        local_command = [sys.executable, str(SCRIPT_DIR / "scan_local_inventory.py"), *roots]
        local_results, local_statuses, payload = run_provider("local", local_command, variant="inventory")
        local_results = local_results[:local_limit]
        local_statuses = [{**status, "resultCount": len(local_results)} for status in local_statuses]
        results.extend(local_results)
        statuses.extend(local_statuses)
        provider_payloads["local"] = payload

    skills_results, skills_statuses, payload = run_provider(
        "skills.sh",
        ["node", str(SCRIPT_DIR / "search_skillssh.mjs"), "search", query],
        variant="search",
    )
    results.extend(skills_results[:limit])
    statuses.extend(skills_statuses)
    provider_payloads["skills.sh"] = payload

    github_results, github_statuses, payload = run_provider(
        "github",
        [
            sys.executable,
            str(SCRIPT_DIR / "search_github.py"),
            query,
            "--live",
            "--type",
            "repositories",
            "--limit",
            str(limit),
            "--token-env",
            github_token_env,
        ],
        variant="repositories",
    )
    results.extend(github_results)
    statuses.extend(github_statuses)
    provider_payloads["github:repositories"] = payload

    if include_github_code:
        github_code_env = None
        token_source = "environment" if os.environ.get(github_token_env) else None
        if not token_source and use_gh_token:
            gh_token = read_gh_auth_token()
            if gh_token:
                github_code_env = {**os.environ, github_token_env: gh_token}
                token_source = "github-cli"
        if token_source:
            code_results, code_statuses, payload = run_provider(
                "github",
                [
                    sys.executable,
                    str(SCRIPT_DIR / "search_github.py"),
                    query,
                    "--live",
                    "--type",
                    "code",
                    "--limit",
                    str(limit),
                    "--token-env",
                    github_token_env,
                ],
                variant="code",
                env=github_code_env,
            )
            for status in code_statuses:
                status["authSource"] = token_source
            results.extend(code_results)
            statuses.extend(code_statuses)
            provider_payloads["github:code"] = payload
        else:
            statuses.append(skipped_status(
                "github",
                f"No {github_token_env} token was available for GitHub code search.",
                variant="code",
                requires_auth=True,
                remediation=[
                    f"Run: python3 {SCRIPT_DIR / 'github_code_auth_helper.py'} --token-env {github_token_env} --use-gh-token",
                    "Confirm GitHub CLI auth with: gh auth status -h github.com.",
                    f"Set {github_token_env} if GitHub CLI auth is unavailable.",
                ],
            ))

    for provider, command, timeout in [
        ("npm", [sys.executable, str(SCRIPT_DIR / "search_npm.py"), "search", query, "--limit", str(limit)], 60),
        ("python", [sys.executable, str(SCRIPT_DIR / "search_python.py"), "search", query, "--limit", str(limit)], 60),
        ("homebrew", [sys.executable, str(SCRIPT_DIR / "search_homebrew.py"), "search", query, "--limit", str(limit)], 90),
        ("hugging-face", [sys.executable, str(SCRIPT_DIR / "search_huggingface.py"), query, "--limit", str(limit)], 90),
    ]:
        provider_results_list, provider_statuses, payload = run_provider(provider, command, variant="search", timeout=timeout)
        results.extend(provider_results_list)
        statuses.extend(provider_statuses)
        provider_payloads[provider] = payload

    plan_payload, plan_error = run_json(
        [sys.executable, str(SCRIPT_DIR / "plan_package_registries.py"), query],
        timeout=20,
    )
    if plan_error:
        statuses.append(error_status("package-registry-plan", plan_error))
    else:
        provider_payloads["packageRegistryPlan"] = plan_payload
        statuses.append(provider_status(
            "package-registry-plan",
            state="queried",
            searched=True,
            reason="Package registry provider plan completed.",
            result_count=0,
        ))
        for provider_plan in (plan_payload or {}).get("providers", []):
            if provider_plan.get("v1Behavior") == "deferred provider plan only":
                statuses.append(provider_status(
                    provider_plan.get("name", "unknown"),
                    state="deferred",
                    searched=False,
                    skipped=True,
                    reason="Provider is planned but deferred in v1.",
                    remediation=["Use the provider plan output before adding live search support."],
                    result_count=0,
                ))

    raw_result_count = len(results)
    results, duplicate_count = dedupe_registry_results(results, dedupe_aliases)
    results = final_rank_results(results)
    skipped = [status for status in statuses if status.get("skipped")]
    return {
        "mode": "all-provider-search",
        "query": query,
        "roots": roots,
        "limitPerProvider": limit,
        "counts": {
            "results": len(results),
            "rawResults": raw_result_count,
            "deduplicatedResults": duplicate_count,
            "dedupeAliasCount": len(dedupe_aliases),
            "providers": len(statuses),
            "skippedProviders": len(skipped),
            "rankedResults": len(results),
        },
        "providerStatus": statuses,
        "skippedProviders": skipped,
        "dedupeAliases": dedupe_aliases,
        "results": results,
        "providerPayloads": provider_payloads,
        "notes": [
            "Provider failures and missing auth are reported without aborting the full search.",
            "Install commands are dry-run recommendations only.",
            "Runtime callable tools require a supplied runtime catalog when this command is run from a shell.",
            "Results are final-ranked after all providers have returned and registry dedupe is complete.",
            "Every all-provider run writes a TOOLS.md implementation shortlist unless --no-tools-md is used.",
            "GitHub code search uses GITHUB_TOKEN or GitHub CLI auth by default when available.",
            "Use --adoption-scope full, partial, feature, or reference to filter candidates by implementation depth.",
            "Pass --report-dir to create TOOLS.md, TOOLS.html, plus media-rich HTML files per source, per tool type, and per source/type pair.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Tool, job, or capability to search for.")
    parser.add_argument("--root", action="append", dest="roots", help="Local root to scan. Repeatable. Defaults to the current directory.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum results per live provider.")
    parser.add_argument("--local-limit", type=int, default=25, help="Maximum local inventory results to include. Use 0 for external-only discovery.")
    parser.add_argument("--runtime-catalog", help="Optional JSON file with callable runtime tools.")
    parser.add_argument("--github-token-env", default="GITHUB_TOKEN", help="Environment variable for GitHub authenticated search.")
    parser.add_argument("--use-gh-token", action="store_true", default=True, help="Use GitHub CLI auth as an ephemeral token source for GitHub code search. Enabled by default.")
    parser.add_argument("--no-gh-token", action="store_false", dest="use_gh_token", help="Do not use GitHub CLI auth as a fallback for GitHub code search.")
    parser.add_argument("--no-github-code", action="store_true", help="Skip GitHub code search even when auth is available.")
    parser.add_argument("--dedupe-aliases", action="append", default=[], help="JSON file with registry dedupe aliases.")
    parser.add_argument("--dedupe-alias", action="append", type=parse_inline_alias, default=[], help="Inline registry dedupe alias, formatted canonical=alias1,alias2.")
    parser.add_argument("--report-dir", help="Write TOOLS.md, TOOLS.html, plus media-rich source, type, and source/type HTML reports to this directory.")
    parser.add_argument("--report-title", default="Tool Finder Results", help="Title for generated report files when --report-dir is used.")
    parser.add_argument("--tools-md", help="Path for the TOOLS.md implementation shortlist. Defaults to <report-dir>/TOOLS.md or ./TOOLS.md.")
    parser.add_argument("--no-tools-md", action="store_true", help="Do not write the default TOOLS.md shortlist.")
    parser.add_argument("--adoption-scope", action="append", default=[], help="Only keep candidates matching an adoption scope: full, partial, feature, or reference. Repeatable.")
    args = parser.parse_args()

    roots = args.roots or [str(Path.cwd())]
    dedupe_aliases = load_dedupe_aliases(args.dedupe_aliases, args.dedupe_alias)
    payload = run_all(
        args.query,
        roots=roots,
        limit=max(1, args.limit),
        local_limit=max(0, args.local_limit),
        runtime_catalog=args.runtime_catalog,
        github_token_env=args.github_token_env,
        include_github_code=not args.no_github_code,
        use_gh_token=args.use_gh_token,
        dedupe_aliases=dedupe_aliases,
    )
    try:
        payload = filter_payload_by_scope(payload, args.adoption_scope)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.report_dir:
        payload["report"] = write_report_bundle(payload, Path(args.report_dir), title=args.report_title)
    if not args.no_tools_md:
        markdown_path = Path(args.tools_md) if args.tools_md else Path(args.report_dir) / "TOOLS.md" if args.report_dir else Path("TOOLS.md")
        existing_markdown = (payload.get("report") or {}).get("toolsMarkdownFile")
        if not existing_markdown or Path(existing_markdown).resolve() != markdown_path.resolve():
            payload["toolsMarkdown"] = write_tools_markdown(payload, markdown_path, title=args.report_title)
        else:
            payload["toolsMarkdown"] = {
                "format": "markdown",
                "toolsMarkdownFile": existing_markdown,
                "filesWritten": [existing_markdown],
            }
    dump_json(payload)


if __name__ == "__main__":
    main()
