#!/usr/bin/env python3
"""Check Tool Finder provider health without installing or modifying tools."""

from __future__ import annotations

import argparse
from pathlib import Path

from search_all_providers import load_dedupe_aliases, parse_inline_alias, run_all
from tool_finder_common import dump_json


def overall_status(statuses: list[dict]) -> str:
    if any(status.get("state") == "error" for status in statuses):
        return "degraded"
    if any(status.get("state") == "skipped" for status in statuses):
        return "partial"
    if any(status.get("state") == "deferred" for status in statuses):
        return "partial"
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="mcp server", help="Small provider query used for the self-check.")
    parser.add_argument("--root", action="append", dest="roots", help="Local root to scan. Defaults to the current directory.")
    parser.add_argument("--runtime-catalog", help="Optional JSON file with callable runtime tools.")
    parser.add_argument("--github-token-env", default="GITHUB_TOKEN", help="Environment variable for GitHub authenticated search.")
    parser.add_argument("--use-gh-token", action="store_true", default=True, help="Use GitHub CLI auth as an ephemeral token source for GitHub code search. Enabled by default.")
    parser.add_argument("--no-gh-token", action="store_false", dest="use_gh_token", help="Do not use GitHub CLI auth as a fallback for GitHub code search.")
    parser.add_argument("--no-github-code", action="store_true", help="Skip GitHub code search even when auth is available.")
    parser.add_argument("--dedupe-aliases", action="append", default=[], help="JSON file with registry dedupe aliases.")
    parser.add_argument("--dedupe-alias", action="append", type=parse_inline_alias, default=[], help="Inline registry dedupe alias, formatted canonical=alias1,alias2.")
    args = parser.parse_args()

    dedupe_aliases = load_dedupe_aliases(args.dedupe_aliases, args.dedupe_alias)
    payload = run_all(
        args.query,
        roots=args.roots or [str(Path.cwd())],
        limit=1,
        local_limit=5,
        runtime_catalog=args.runtime_catalog,
        github_token_env=args.github_token_env,
        include_github_code=not args.no_github_code,
        use_gh_token=args.use_gh_token,
        dedupe_aliases=dedupe_aliases,
    )
    statuses = payload.get("providerStatus") or []
    checks = [
        {
            "provider": status.get("provider"),
            "variant": status.get("variant"),
            "state": status.get("state"),
            "searched": status.get("searched"),
            "skipped": status.get("skipped"),
            "requiresAuth": status.get("requiresAuth"),
            "authSource": status.get("authSource"),
            "reason": status.get("reason"),
            "resultCount": status.get("resultCount"),
            "remediation": status.get("remediation") or [],
        }
        for status in statuses
    ]
    dump_json({
        "mode": "tool-finder-self-check",
        "status": overall_status(checks),
        "query": args.query,
        "summary": {
            "checks": len(checks),
            "queried": sum(1 for check in checks if check.get("searched")),
            "skipped": sum(1 for check in checks if check.get("skipped")),
            "errors": sum(1 for check in checks if check.get("state") == "error"),
            "results": payload.get("counts", {}).get("results", 0),
        },
        "checks": checks,
        "notes": [
            "Self-check uses the same provider path as the all-provider command.",
            "Skipped auth-gated providers are reported as partial health, not command failure.",
            "No installs, writes, or package updates are executed.",
        ],
    })


if __name__ == "__main__":
    main()
