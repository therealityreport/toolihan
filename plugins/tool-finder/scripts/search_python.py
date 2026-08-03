#!/usr/bin/env python3
"""Unified Python package metadata and pip/pipx install-plan provider."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

from search_pips import dry_run_command, install_command, requirement_name
from search_pypi import (
    fetch_project,
    latest_upload_time,
    looks_like_cli,
    project_url,
    simple_project_url,
)
from tool_finder_common import dump_json, normalize_result, score_result, unique


def choose_installer(info: dict[str, Any], requested: str) -> str:
    if requested != "auto":
        return requested
    return "pipx" if looks_like_cli(info) else "pip"


def choose_repo(info: dict[str, Any]) -> str | None:
    project_urls = info.get("project_urls") if isinstance(info.get("project_urls"), dict) else {}
    for key in ("Source", "Source Code", "Repository", "Homepage", "Bug Tracker"):
        if project_urls.get(key):
            return project_urls[key]
    return info.get("home_page") or None


def normalize_python_project(
    payload: dict[str, Any],
    *,
    requirement: str | None = None,
    installer: str = "auto",
    api_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    info = payload.get("info") or {}
    name = info.get("name") or requirement_name(requirement or "unknown")
    requirement_value = requirement or name
    selected_installer = choose_installer(info, installer)
    is_cli = selected_installer == "pipx" or looks_like_cli(info)
    upload_time = latest_upload_time(payload)
    vulnerabilities = payload.get("vulnerabilities") or []
    risk_notes = [
        "Python package install is not executed automatically.",
        "PyPI metadata and pip/pipx install planning are shown together in this unified Python provider.",
    ]
    if selected_installer == "pip":
        risk_notes.append("pip installs into the selected Python environment; prefer a virtual environment for project dependencies.")
    else:
        risk_notes.append("pipx is intended for Python applications with command-line entry points.")
    if vulnerabilities:
        risk_notes.append(f"PyPI reports {len(vulnerabilities)} known vulnerability record(s) for this response.")
    command = install_command(requirement_value, selected_installer)
    result = normalize_result(
        name=name,
        asset_type="cli" if is_cli else "library",
        source="python",
        path=requirement_value,
        url=f"https://pypi.org/project/{name}/",
        repo=choose_repo(info),
        status="installable",
        action="dry-run-install-plan",
        reasons=[
            reason
            for reason in [
                info.get("summary") or "Discovered from PyPI project metadata.",
                f"Installer: {selected_installer}.",
                f"Latest version: {info.get('version')}." if info.get("version") else "",
                f"Requires Python: {info.get('requires_python')}." if info.get("requires_python") else "",
                "Metadata suggests command-line usage." if looks_like_cli(info) else "",
            ]
            if reason
        ],
        risks=risk_notes,
        install_command=command,
        install_url=f"https://pypi.org/project/{name}/",
        source_trust="registry",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "python-package",
            "pypiName": name,
            "pypiVersion": info.get("version"),
            "installer": selected_installer,
        },
        safety={
            "status": "warn" if vulnerabilities else "unknown",
            "riskLevel": "medium" if vulnerabilities else "unknown",
            "notes": risk_notes,
        },
        maintenance={
            "lastUpdated": upload_time,
            "signals": [
                signal
                for signal in [
                    f"latest-upload:{upload_time}" if upload_time else None,
                    f"requires-python:{info.get('requires_python')}" if info.get("requires_python") else None,
                    f"classifiers:{len(info.get('classifiers') or [])}",
                ]
                if signal
            ],
        },
        api_evidence={
            "searchType": "python-package",
            **(api_evidence or {}),
        },
    )
    result["install"]["installer"] = selected_installer
    result["install"]["dryRunCommand"] = dry_run_command(requirement_value, selected_installer)
    result["install"]["fallbackCommand"] = install_command(requirement_value, "pip" if selected_installer == "pipx" else "pipx")
    result["capabilities"] = [
        value
        for value in [
            info.get("summary"),
            f"requires-python: {info.get('requires_python')}" if info.get("requires_python") else None,
            f"keywords: {info.get('keywords')}" if info.get("keywords") else None,
            f"pip dry-run: {result['install']['dryRunCommand']}" if result["install"]["dryRunCommand"] else None,
        ]
        if value
    ]
    result["providerViews"] = {
        "pypi": {
            "name": name,
            "version": info.get("version"),
            "summary": info.get("summary"),
            "requiresPython": info.get("requires_python"),
            "projectUrl": f"https://pypi.org/project/{name}/",
            "jsonUrl": project_url(name),
            "simpleIndexUrl": simple_project_url(name),
            "vulnerabilityCount": len(vulnerabilities),
        },
        "installPlan": {
            "installer": selected_installer,
            "command": command,
            "dryRunCommand": result["install"]["dryRunCommand"],
            "fallbackCommand": result["install"]["fallbackCommand"],
        },
    }
    return score_result(result)


def detail(requirement: str, installer: str) -> dict[str, Any]:
    name = requirement_name(requirement)
    payload, evidence = fetch_project(name)
    return {
        "mode": "python-live-detail",
        "provider": "python",
        "requirement": requirement,
        "result": normalize_python_project(payload, requirement=requirement, installer=installer, api_evidence={**evidence, "searchType": "detail"}),
        "pypiJsonUrl": project_url(name),
        "simpleIndexUrl": simple_project_url(name),
        "notes": [
            "Unified Python provider combines PyPI metadata and pip/pipx install plans.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def search(query: str, limit: int, installer: str) -> dict[str, Any]:
    candidates = unique([token for token in re.split(r"[\s,;]+", query) if token] + [query.strip()])
    results = []
    misses = []
    for candidate in candidates[:limit]:
        try:
            payload, evidence = fetch_project(requirement_name(candidate))
        except SystemExit:
            misses.append(candidate)
            continue
        result = normalize_python_project(payload, requirement=candidate, installer=installer, api_evidence={**evidence, "searchQuery": query})
        result["reasons"] = unique(result.get("reasons", []) + ["Python provider matched an exact PyPI project-name candidate."])
        results.append(result)
    return {
        "mode": "python-live-search",
        "provider": "python",
        "query": query,
        "installer": installer,
        "results": results,
        "misses": misses,
        "notes": [
            "PyPI's official JSON API is project-oriented, so search checks exact project-name candidates.",
            "Unified Python provider combines PyPI metadata and pip/pipx install plans.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Resolve exact Python package candidates.")
    search_parser.add_argument("query", help="Project name, requirement, or candidate words.")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--installer", choices=["auto", "pip", "pipx"], default="auto")

    detail_parser = subparsers.add_parser("detail", help="Fetch one Python package and install plan.")
    detail_parser.add_argument("requirement", help="Package name or requirement string.")
    detail_parser.add_argument("--installer", choices=["auto", "pip", "pipx"], default="auto")

    plan_parser = subparsers.add_parser("plan", help="Alias for detail.")
    plan_parser.add_argument("requirement", help="Package name or requirement string.")
    plan_parser.add_argument("--installer", choices=["auto", "pip", "pipx"], default="auto")

    args = parser.parse_args()
    if args.command == "search":
        dump_json(search(args.query, max(1, args.limit), args.installer))
        return
    if args.command in {"detail", "plan"}:
        dump_json(detail(args.requirement, args.installer))
        return
    parser.print_help(sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
