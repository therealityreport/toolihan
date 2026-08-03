#!/usr/bin/env python3
"""Search Homebrew formula/cask metadata and emit normalized Tool Finder results."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from tool_finder_common import dump_json, normalize_result, score_result, unique


API_BASE = "https://formulae.brew.sh/api"
SITE_BASE = "https://formulae.brew.sh"
USER_AGENT = "tool-finder/0.1 (+https://formulae.brew.sh/docs/api/)"


def request_json(url: str, *, timeout: int = 30) -> tuple[Any, dict[str, str | None]]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), headers_to_evidence(response.headers)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:4000]
        raise SystemExit(json.dumps({
            "error": "Homebrew request failed",
            "status": error.code,
            "url": url,
            "body": body,
        }, indent=2))
    except urllib.error.URLError as error:
        raise SystemExit(json.dumps({
            "error": "Homebrew request failed",
            "url": url,
            "reason": str(error.reason),
        }, indent=2))


def headers_to_evidence(headers: Any) -> dict[str, str | None]:
    return {
        "rateLimitRemaining": headers.get("X-RateLimit-Remaining"),
        "cacheUntil": headers.get("Cache-Control"),
        "etag": headers.get("ETag"),
        "lastModified": headers.get("Last-Modified"),
    }


def api_name(name: str) -> str:
    return urllib.parse.quote(name, safe="@+-.")


def formula_list_url() -> str:
    return f"{API_BASE}/formula.json"


def cask_list_url() -> str:
    return f"{API_BASE}/cask.json"


def formula_detail_url(name: str) -> str:
    return f"{API_BASE}/formula/{api_name(name)}.json"


def cask_detail_url(token: str) -> str:
    return f"{API_BASE}/cask/{api_name(token)}.json"


def formula_page(name: str) -> str:
    return f"{SITE_BASE}/formula/{urllib.parse.quote(name, safe='@+-.')}"


def cask_page(token: str) -> str:
    return f"{SITE_BASE}/cask/{urllib.parse.quote(token, safe='@+-.')}"


def text_blob(item: dict[str, Any], kind: str) -> str:
    fields: list[Any]
    if kind == "formula":
        fields = [
            item.get("name"),
            item.get("full_name"),
            item.get("desc"),
            item.get("homepage"),
            " ".join(item.get("aliases") or []),
            " ".join(item.get("executables") or []),
        ]
    else:
        fields = [
            item.get("token"),
            item.get("full_token"),
            " ".join(item.get("name") or []),
            item.get("desc"),
            item.get("homepage"),
            " ".join(item.get("old_tokens") or []),
        ]
    return " ".join(str(field) for field in fields if field).lower()


def match_score(item: dict[str, Any], query: str, kind: str) -> int:
    query_lower = query.lower().strip()
    tokens = [token for token in query_lower.replace("_", "-").split() if token]
    primary = (item.get("name") if kind == "formula" else item.get("token")) or ""
    primary_lower = str(primary).lower()
    blob = text_blob(item, kind)
    score = 0
    if primary_lower == query_lower:
        score += 100
    elif primary_lower.startswith(query_lower):
        score += 80
    elif query_lower in blob:
        score += 60
    if tokens:
        score += sum(10 for token in tokens if token in blob)
        if all(token in blob for token in tokens):
            score += 20
    return score


def analytics_installs(item: dict[str, Any]) -> int | None:
    analytics = item.get("analytics") or {}
    candidates = [
        analytics.get("install_on_request", {}).get("30d") if isinstance(analytics.get("install_on_request"), dict) else None,
        analytics.get("install", {}).get("30d") if isinstance(analytics.get("install"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = candidate.get(item.get("name") or item.get("token"))
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and candidate.isdigit():
            return int(candidate)
    return None


def normalize_formula(item: dict[str, Any], api_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    name = item.get("name") or item.get("full_name") or "unknown-formula"
    executables = item.get("executables") or []
    version = (item.get("versions") or {}).get("stable") or (item.get("versions") or {}).get("head")
    disabled = bool(item.get("disabled"))
    deprecated = bool(item.get("deprecated"))
    risk_notes = ["Homebrew install is not executed automatically."]
    if item.get("post_install_defined") or item.get("post_install_steps"):
        risk_notes.append("Formula defines post-install behavior.")
    if deprecated:
        risk_notes.append("Formula is deprecated.")
    if disabled:
        risk_notes.append("Formula is disabled.")
    reasons = [
        item.get("desc") or "Discovered from Homebrew formula metadata.",
        f"Stable version: {version}." if version else "",
        f"Executables: {', '.join(executables[:5])}." if executables else "",
        f"License: {item.get('license')}." if item.get("license") else "",
    ]
    result = normalize_result(
        name=name,
        asset_type="cli" if executables else "unknown",
        source="homebrew",
        path=name,
        url=formula_page(name),
        repo=item.get("tap"),
        status="installable" if not disabled else "manual",
        action="dry-run-install-plan",
        reasons=[reason for reason in reasons if reason],
        risks=risk_notes,
        install_command=f"brew install {name}",
        install_url=formula_page(name),
        source_trust="registry",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "homebrew-formula",
            "homebrewName": name,
            "homebrewVersion": version,
        },
        safety={
            "status": "warn" if (disabled or deprecated) else "unknown",
            "riskLevel": "medium" if (disabled or deprecated) else "unknown",
            "notes": risk_notes,
        },
        maintenance={
            "lastUpdated": item.get("generated_date"),
            "installs": analytics_installs(item),
            "signals": [
                signal
                for signal in [
                    f"tap:{item.get('tap')}" if item.get("tap") else None,
                    f"bottle:{bool((item.get('versions') or {}).get('bottle'))}",
                    f"deprecated:{deprecated}",
                    f"disabled:{disabled}",
                ]
                if signal is not None
            ],
        },
        api_evidence={
            "searchType": "homebrew-formula",
            **(api_evidence or {}),
        },
    )
    result["capabilities"] = [
        value
        for value in [
            item.get("desc"),
            f"executables: {', '.join(executables)}" if executables else None,
            f"dependencies: {', '.join((item.get('dependencies') or [])[:8])}" if item.get("dependencies") else None,
        ]
        if value
    ]
    return score_result(result)


def normalize_cask(item: dict[str, Any], api_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    token = item.get("token") or item.get("full_token") or "unknown-cask"
    names = item.get("name") or []
    display_name = names[0] if names else token
    disabled = bool(item.get("disabled"))
    deprecated = bool(item.get("deprecated"))
    risk_notes = ["Homebrew cask install is not executed automatically."]
    artifacts = item.get("artifacts") or []
    if artifacts:
        risk_notes.append("Cask may create app artifacts or uninstall actions.")
    if deprecated:
        risk_notes.append("Cask is deprecated.")
    if disabled:
        risk_notes.append("Cask is disabled.")
    reasons = [
        item.get("desc") or "Discovered from Homebrew cask metadata.",
        f"Version: {item.get('version')}." if item.get("version") else "",
        f"Names: {', '.join(names[:3])}." if names else "",
    ]
    result = normalize_result(
        name=display_name,
        asset_type="app",
        source="homebrew",
        path=token,
        url=cask_page(token),
        repo=item.get("tap"),
        status="installable" if not disabled else "manual",
        action="dry-run-install-plan",
        reasons=[reason for reason in reasons if reason],
        risks=risk_notes,
        install_command=f"brew install --cask {token}",
        install_url=cask_page(token),
        source_trust="registry",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "homebrew-cask",
            "homebrewToken": token,
            "homebrewVersion": item.get("version"),
        },
        safety={
            "status": "warn" if (disabled or deprecated) else "unknown",
            "riskLevel": "medium" if (disabled or deprecated) else "unknown",
            "notes": risk_notes,
        },
        maintenance={
            "lastUpdated": item.get("generated_date"),
            "installs": analytics_installs(item),
            "signals": [
                signal
                for signal in [
                    f"tap:{item.get('tap')}" if item.get("tap") else None,
                    f"deprecated:{deprecated}",
                    f"disabled:{disabled}",
                ]
                if signal is not None
            ],
        },
        api_evidence={
            "searchType": "homebrew-cask",
            **(api_evidence or {}),
        },
    )
    result["capabilities"] = [
        value
        for value in [
            item.get("desc"),
            f"names: {', '.join(names)}" if names else None,
            f"artifacts: {len(artifacts)}" if artifacts else None,
        ]
        if value
    ]
    return score_result(result)


def fetch_formula(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, evidence = request_json(formula_detail_url(name))
    if not isinstance(payload, dict):
        raise SystemExit("Homebrew formula detail response was not an object.")
    return payload, evidence


def fetch_cask(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, evidence = request_json(cask_detail_url(token))
    if not isinstance(payload, dict):
        raise SystemExit("Homebrew cask detail response was not an object.")
    return payload, evidence


def fetch_list(kind: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload, evidence = request_json(formula_list_url() if kind == "formula" else cask_list_url())
    if not isinstance(payload, list):
        raise SystemExit("Homebrew list response was not an array.")
    return payload, evidence


def detail(name: str, kind: str) -> dict[str, Any]:
    results = []
    misses = []
    if kind in {"formula", "all"}:
        try:
            payload, evidence = fetch_formula(name)
            results.append(normalize_formula(payload, {**evidence, "searchType": "detail"}))
        except SystemExit:
            misses.append(f"formula:{name}")
    if kind in {"cask", "all"}:
        try:
            payload, evidence = fetch_cask(name)
            results.append(normalize_cask(payload, {**evidence, "searchType": "detail"}))
        except SystemExit:
            misses.append(f"cask:{name}")
    return {
        "mode": "homebrew-live-detail",
        "provider": "homebrew",
        "query": name,
        "kind": kind,
        "results": results,
        "misses": misses,
        "notes": ["Uses the Homebrew formulae.brew.sh JSON API.", "Install commands are dry-run recommendations only."],
    }


def search(query: str, kind: str, limit: int) -> dict[str, Any]:
    candidates: list[tuple[int, dict[str, Any], str, dict[str, Any]]] = []
    kinds = ["formula", "cask"] if kind == "all" else [kind]
    for current_kind in kinds:
        items, evidence = fetch_list(current_kind)
        for item in items:
            score = match_score(item, query, current_kind)
            if score > 0:
                candidates.append((score, item, current_kind, evidence))
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    results = []
    for match, item, current_kind, evidence in candidates[:limit]:
        normalizer = normalize_formula if current_kind == "formula" else normalize_cask
        result = normalizer(item, {**evidence, "searchQuery": query, "matchScore": str(match)})
        result["reasons"] = unique(result.get("reasons", []) + [f"Homebrew metadata match score: {match}."])
        results.append(result)
    return {
        "mode": "homebrew-live-search",
        "provider": "homebrew",
        "query": query,
        "kind": kind,
        "results": results,
        "notes": [
            "Uses Homebrew formula and cask JSON metadata.",
            "Search downloads metadata lists and filters locally.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search Homebrew formulae and casks.")
    search_parser.add_argument("query", help="Formula, cask, CLI, app, or capability terms.")
    search_parser.add_argument("--kind", choices=["formula", "cask", "all"], default="all")
    search_parser.add_argument("--limit", type=int, default=10)

    detail_parser = subparsers.add_parser("detail", help="Fetch one formula or cask.")
    detail_parser.add_argument("name", help="Formula name or cask token.")
    detail_parser.add_argument("--kind", choices=["formula", "cask", "all"], default="all")

    args = parser.parse_args()
    if args.command == "search":
        dump_json(search(args.query, args.kind, max(1, args.limit)))
        return
    if args.command == "detail":
        dump_json(detail(args.name, args.kind))
        return
    parser.print_help(sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
