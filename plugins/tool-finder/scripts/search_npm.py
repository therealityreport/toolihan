#!/usr/bin/env python3
"""Search npm's public registry and emit normalized Tool Finder results."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from tool_finder_common import dump_json, normalize_result, score_result


REGISTRY_BASE = "https://registry.npmjs.org"
SEARCH_URL = f"{REGISTRY_BASE}/-/v1/search"
USER_AGENT = "tool-finder/0.1 (+https://github.com/npm/registry)"


def request_json(url: str, *, timeout: int = 20) -> tuple[dict[str, Any], dict[str, str | None]]:
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
            "error": "npm request failed",
            "status": error.code,
            "url": url,
            "body": body,
        }, indent=2))
    except urllib.error.URLError as error:
        raise SystemExit(json.dumps({
            "error": "npm request failed",
            "url": url,
            "reason": str(error.reason),
        }, indent=2))


def headers_to_evidence(headers: Any) -> dict[str, str | None]:
    return {
        "rateLimitRemaining": headers.get("X-RateLimit-Remaining"),
        "cacheUntil": headers.get("Cache-Control"),
        "etag": headers.get("ETag"),
    }


def package_url(name: str) -> str:
    return f"{REGISTRY_BASE}/{urllib.parse.quote(name, safe='@')}"


def search_url(query: str, limit: int, offset: int) -> str:
    params = urllib.parse.urlencode({
        "text": query,
        "size": limit,
        "from": offset,
    })
    return f"{SEARCH_URL}?{params}"


def latest_document(metadata: dict[str, Any]) -> dict[str, Any]:
    latest_version = (metadata.get("dist-tags") or {}).get("latest")
    versions = metadata.get("versions") or {}
    if latest_version and isinstance(versions, dict):
        latest = versions.get(latest_version)
        if isinstance(latest, dict):
            return latest
    return {}


def normalize_repository(repository: Any) -> str | None:
    if isinstance(repository, str):
        return repository
    if isinstance(repository, dict):
        return repository.get("url")
    return None


def extract_bin(package: dict[str, Any], detail: dict[str, Any] | None = None) -> Any:
    if detail:
        latest = latest_document(detail)
        if "bin" in latest:
            return latest.get("bin")
    return package.get("bin")


def looks_like_cli(package: dict[str, Any], bin_value: Any) -> bool:
    if bin_value:
        return True
    haystack = " ".join(str(value) for value in [
        package.get("name"),
        package.get("description"),
        " ".join(package.get("keywords") or []),
    ]).lower()
    return any(token in haystack for token in (" cli", "command line", "command-line", "terminal", "bin "))


def normalize_npm_package(
    package: dict[str, Any],
    *,
    detail: dict[str, Any] | None = None,
    search_score: float | None = None,
    api_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    name = package.get("name") or (detail or {}).get("name") or "unknown-npm-package"
    latest = latest_document(detail or {})
    version = package.get("version") or latest.get("version") or (detail or {}).get("dist-tags", {}).get("latest")
    links = package.get("links") or {}
    repo_url = links.get("repository") or normalize_repository(latest.get("repository") or (detail or {}).get("repository"))
    npm_url = links.get("npm") or f"https://www.npmjs.com/package/{urllib.parse.quote(name, safe='@/')}"
    bin_value = extract_bin(package, detail)
    is_cli = looks_like_cli({**package, **latest}, bin_value)
    install_command = f"npm install -g {name}" if is_cli else f"npm install {name}"
    reasons = [
        package.get("description") or latest.get("description") or "Discovered from npm registry metadata.",
        "Package exposes a bin entry." if bin_value else "",
        f"Latest version: {version}." if version else "",
    ]
    if search_score is not None:
        reasons.append(f"npm search score: {search_score:.3f}.")
    maintenance_signals: list[str] = []
    if package.get("date"):
        maintenance_signals.append(f"published-or-updated:{package['date']}")
    if detail and (detail.get("time") or {}).get("modified"):
        maintenance_signals.append(f"modified:{detail['time']['modified']}")
    result = normalize_result(
        name=name,
        asset_type="cli" if is_cli else "unknown",
        source="npm",
        path=name,
        url=npm_url,
        repo=repo_url,
        status="installable",
        action="dry-run-install-plan",
        reasons=[reason for reason in reasons if reason],
        risks=["Registry package install is not executed automatically."],
        install_command=install_command,
        install_url=npm_url,
        source_trust="registry",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "npm",
            "npmName": name,
            "npmVersion": version,
        },
        safety={
            "status": "unknown",
            "riskLevel": "unknown",
            "notes": ["Inspect package scripts and transitive dependencies before installing globally."],
        },
        maintenance={
            "lastUpdated": package.get("date") or (detail or {}).get("time", {}).get("modified"),
            "signals": maintenance_signals,
        },
        api_evidence={
            "searchType": "registry",
            **(api_evidence or {}),
        },
    )
    result["capabilities"] = [
        value
        for value in [
            package.get("description") or latest.get("description"),
            f"keywords: {', '.join(package.get('keywords') or [])}" if package.get("keywords") else None,
        ]
        if value
    ]
    return score_result(result)


def fetch_detail(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    return request_json(package_url(name))


def search(query: str, *, limit: int, offset: int, enrich_details: bool) -> dict[str, Any]:
    data, evidence = request_json(search_url(query, limit, offset))
    results = []
    for hit in data.get("objects") or []:
        package = hit.get("package") or {}
        detail = None
        detail_evidence = {}
        if enrich_details and package.get("name"):
            try:
                detail, detail_evidence = fetch_detail(package["name"])
            except SystemExit:
                detail = None
        results.append(normalize_npm_package(
            package,
            detail=detail,
            search_score=hit.get("searchScore"),
            api_evidence={**evidence, **detail_evidence, "searchQuery": query},
        ))
    return {
        "mode": "npm-live-search",
        "query": query,
        "provider": "npm",
        "results": results,
        "total": data.get("total"),
        "notes": [
            "Uses npm registry metadata and search endpoints.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def detail(name: str) -> dict[str, Any]:
    data, evidence = fetch_detail(name)
    latest = latest_document(data)
    package = {
        "name": data.get("name") or name,
        "version": latest.get("version") or (data.get("dist-tags") or {}).get("latest"),
        "description": latest.get("description") or data.get("description"),
        "keywords": latest.get("keywords") or data.get("keywords") or [],
        "links": {
            "npm": f"https://www.npmjs.com/package/{urllib.parse.quote(name, safe='@/')}",
            "repository": normalize_repository(latest.get("repository") or data.get("repository")),
            "homepage": latest.get("homepage") or data.get("homepage"),
        },
        "date": (data.get("time") or {}).get("modified"),
    }
    return {
        "mode": "npm-live-detail",
        "provider": "npm",
        "result": normalize_npm_package(package, detail=data, api_evidence={**evidence, "searchType": "detail"}),
        "rawVersion": latest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search npm packages.")
    search_parser.add_argument("query", help="Search terms.")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum results, capped at 250.")
    search_parser.add_argument("--offset", type=int, default=0)
    search_parser.add_argument("--no-enrich-details", action="store_true", help="Skip per-package metadata lookups.")

    detail_parser = subparsers.add_parser("detail", help="Fetch one npm package.")
    detail_parser.add_argument("name", help="Package name, including scope if needed.")

    args = parser.parse_args()
    if args.command == "search":
        limit = max(1, min(args.limit, 250))
        dump_json(search(args.query, limit=limit, offset=max(args.offset, 0), enrich_details=not args.no_enrich_details))
        return
    if args.command == "detail":
        dump_json(detail(args.name))
        return
    parser.print_help(sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
