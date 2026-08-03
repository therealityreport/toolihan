#!/usr/bin/env python3
"""Search PyPI project metadata and emit normalized Tool Finder results."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from tool_finder_common import dump_json, normalize_result, score_result, unique


PYPI_BASE = "https://pypi.org"
USER_AGENT = "tool-finder/0.1 (+https://docs.pypi.org/api/json/)"


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
            "error": "PyPI request failed",
            "status": error.code,
            "url": url,
            "body": body,
        }, indent=2))
    except urllib.error.URLError as error:
        raise SystemExit(json.dumps({
            "error": "PyPI request failed",
            "url": url,
            "reason": str(error.reason),
        }, indent=2))


def headers_to_evidence(headers: Any) -> dict[str, str | None]:
    return {
        "rateLimitRemaining": headers.get("X-RateLimit-Remaining"),
        "cacheUntil": headers.get("Cache-Control"),
        "lastSerial": headers.get("X-PyPI-Last-Serial"),
    }


def project_url(name: str) -> str:
    return f"{PYPI_BASE}/pypi/{urllib.parse.quote(name)}/json"


def simple_project_url(name: str) -> str:
    return f"{PYPI_BASE}/simple/{urllib.parse.quote(name)}/"


def tokenize_candidates(query: str, limit: int) -> list[str]:
    tokens = [
        token.strip("._- ")
        for token in re.split(r"[\s,;]+", query)
        if token.strip("._- ")
    ]
    candidates = unique(tokens + [query.strip()])
    return candidates[:limit]


def looks_like_cli(info: dict[str, Any]) -> bool:
    values = [
        info.get("name"),
        info.get("summary"),
        info.get("keywords"),
        " ".join(info.get("classifiers") or []),
    ]
    haystack = " ".join(str(value) for value in values if value).lower()
    return any(token in haystack for token in (" cli", "command line", "command-line", "terminal", "console", "shell"))


def choose_repo(project_urls: dict[str, str] | None, home_page: str | None) -> str | None:
    if project_urls:
        for key in ("Source", "Source Code", "Repository", "Homepage", "Bug Tracker"):
            if project_urls.get(key):
                return project_urls[key]
        for value in project_urls.values():
            if value:
                return value
    return home_page or None


def latest_upload_time(payload: dict[str, Any]) -> str | None:
    latest = (payload.get("info") or {}).get("version")
    releases = payload.get("releases") or {}
    files = releases.get(latest) if latest else None
    if not files:
        files = payload.get("urls") or []
    times = [item.get("upload_time_iso_8601") or item.get("upload_time") for item in files if item.get("upload_time") or item.get("upload_time_iso_8601")]
    return max(times) if times else None


def normalize_pypi_project(payload: dict[str, Any], api_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    info = payload.get("info") or {}
    name = info.get("name") or "unknown-pypi-project"
    project_urls = info.get("project_urls") if isinstance(info.get("project_urls"), dict) else {}
    homepage = info.get("home_page") or info.get("project_url") or f"https://pypi.org/project/{urllib.parse.quote(name)}/"
    repo = choose_repo(project_urls, info.get("home_page"))
    is_cli = looks_like_cli(info)
    upload_time = latest_upload_time(payload)
    vulnerabilities = payload.get("vulnerabilities") or []
    reasons = [
        info.get("summary") or "Discovered from PyPI project metadata.",
        f"Latest version: {info.get('version')}." if info.get("version") else "",
        f"Requires Python: {info.get('requires_python')}." if info.get("requires_python") else "",
        "Metadata suggests command-line usage." if is_cli else "",
    ]
    risk_notes = ["Registry package install is not executed automatically."]
    if vulnerabilities:
        risk_notes.append(f"PyPI reports {len(vulnerabilities)} known vulnerability record(s) for this response.")
    result = normalize_result(
        name=name,
        asset_type="cli" if is_cli else "unknown",
        source="pypi",
        path=name,
        url=homepage,
        repo=repo,
        status="installable",
        action="dry-run-install-plan",
        reasons=[reason for reason in reasons if reason],
        risks=risk_notes,
        install_command=f"pipx install {name}" if is_cli else f"pip install {name}",
        install_url=homepage,
        source_trust="registry",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "pypi",
            "pypiName": name,
            "pypiVersion": info.get("version"),
        },
        safety={
            "status": "warn" if vulnerabilities else "unknown",
            "riskLevel": "medium" if vulnerabilities else "unknown",
            "notes": risk_notes + ["PyPI JSON metadata does not expose console_scripts; inspect package files before installing."],
        },
        maintenance={
            "lastUpdated": upload_time,
            "signals": [
                signal
                for signal in [
                    f"latest-upload:{upload_time}" if upload_time else None,
                    f"classifiers:{len(info.get('classifiers') or [])}",
                ]
                if signal
            ],
        },
        api_evidence={
            "searchType": "project-metadata",
            **(api_evidence or {}),
        },
    )
    result["capabilities"] = [
        value
        for value in [
            info.get("summary"),
            f"keywords: {info.get('keywords')}" if info.get("keywords") else None,
            f"classifiers: {', '.join((info.get('classifiers') or [])[:5])}" if info.get("classifiers") else None,
        ]
        if value
    ]
    return score_result(result)


def fetch_project(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    return request_json(project_url(name))


def detail(name: str) -> dict[str, Any]:
    payload, evidence = fetch_project(name)
    return {
        "mode": "pypi-live-detail",
        "provider": "pypi",
        "result": normalize_pypi_project(payload, {**evidence, "searchType": "detail"}),
        "simpleIndexUrl": simple_project_url(name),
    }


def search(query: str, limit: int) -> dict[str, Any]:
    results = []
    misses = []
    for candidate in tokenize_candidates(query, limit):
        try:
            payload, evidence = fetch_project(candidate)
        except SystemExit:
            misses.append(candidate)
            continue
        result = normalize_pypi_project(payload, {**evidence, "searchQuery": query})
        result["reasons"] = unique(result.get("reasons", []) + ["PyPI provider matched an exact project-name candidate."])
        results.append(result)
    return {
        "mode": "pypi-live-search",
        "query": query,
        "provider": "pypi",
        "results": results,
        "misses": misses,
        "notes": [
            "PyPI's official JSON API is project-oriented, so search checks exact project-name candidates.",
            "Use detail mode when the package name is known.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Resolve exact PyPI project-name candidates from a query.")
    search_parser.add_argument("query", help="Project name or candidate words.")
    search_parser.add_argument("--limit", type=int, default=10)

    detail_parser = subparsers.add_parser("detail", help="Fetch one PyPI project.")
    detail_parser.add_argument("name", help="Project name.")

    args = parser.parse_args()
    if args.command == "search":
        dump_json(search(args.query, max(1, args.limit)))
        return
    if args.command == "detail":
        dump_json(detail(args.name))
        return
    parser.print_help(sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
