#!/usr/bin/env python3
"""Plan pip and pipx installs from PyPI metadata for Tool Finder."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

from search_pypi import fetch_project, latest_upload_time, looks_like_cli, project_url, simple_project_url
from tool_finder_common import dump_json, normalize_result, score_result, unique


REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def requirement_name(requirement: str) -> str:
    match = REQUIREMENT_NAME_RE.match(requirement)
    if not match:
        raise SystemExit(f"Could not parse package name from requirement: {requirement}")
    return match.group(1)


def choose_installer(info: dict[str, Any], requested: str) -> str:
    if requested != "auto":
        return requested
    return "pipx" if looks_like_cli(info) else "pip"


def install_command(requirement: str, installer: str) -> str:
    if installer == "pipx":
        return f"pipx install {requirement}"
    return f"python -m pip install {requirement}"


def dry_run_command(requirement: str, installer: str) -> str | None:
    if installer == "pipx":
        return None
    return f"python -m pip install --dry-run --report - {requirement}"


def normalize_pips_project(
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
    risk_notes = ["Python package install is not executed automatically."]
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
        source="pips",
        path=requirement_value,
        url=f"https://pypi.org/project/{name}/",
        repo=(info.get("project_urls") or {}).get("Source") if isinstance(info.get("project_urls"), dict) else info.get("home_page"),
        status="installable",
        action="dry-run-install-plan",
        reasons=[
            reason
            for reason in [
                info.get("summary") or "Planned from PyPI project metadata.",
                f"Installer: {selected_installer}.",
                f"Latest version: {info.get('version')}." if info.get("version") else "",
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
            "sourceType": "python-installer",
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
                ]
                if signal
            ],
        },
        api_evidence={
            "searchType": "python-installer-plan",
            **(api_evidence or {}),
        },
    )
    result["install"]["dryRunCommand"] = dry_run_command(requirement_value, selected_installer)
    result["install"]["fallbackCommand"] = install_command(requirement_value, "pip" if selected_installer == "pipx" else "pipx")
    result["capabilities"] = [
        value
        for value in [
            info.get("summary"),
            f"requires-python: {info.get('requires_python')}" if info.get("requires_python") else None,
            f"pip dry-run: {result['install']['dryRunCommand']}" if result["install"]["dryRunCommand"] else None,
        ]
        if value
    ]
    return score_result(result)


def detail(requirement: str, installer: str) -> dict[str, Any]:
    name = requirement_name(requirement)
    payload, evidence = fetch_project(name)
    return {
        "mode": "pips-live-detail",
        "provider": "pips",
        "requirement": requirement,
        "result": normalize_pips_project(payload, requirement=requirement, installer=installer, api_evidence={**evidence, "searchType": "detail"}),
        "pypiJsonUrl": project_url(name),
        "simpleIndexUrl": simple_project_url(name),
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
        result = normalize_pips_project(payload, requirement=candidate, installer=installer, api_evidence={**evidence, "searchQuery": query})
        result["reasons"] = unique(result.get("reasons", []) + ["pips provider matched an exact PyPI project-name candidate."])
        results.append(result)
    return {
        "mode": "pips-live-search",
        "provider": "pips",
        "query": query,
        "installer": installer,
        "results": results,
        "misses": misses,
        "notes": [
            "pips is Tool Finder's Python installer-plan provider.",
            "It uses PyPI project metadata, pip install syntax, and pip dry-run reports where pip is selected.",
            "pipx plans are recommended for CLI-shaped Python applications.",
            "Install commands are dry-run recommendations only.",
        ],
    }


def plan(requirement: str, installer: str) -> dict[str, Any]:
    return detail(requirement, installer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name, help_text in (
        ("search", "Resolve exact PyPI candidates and produce pip/pipx plans."),
        ("detail", "Fetch one PyPI project and produce a pip/pipx plan."),
        ("plan", "Alias for detail, accepting a requirement string."),
    ):
        command_parser = subparsers.add_parser(command_name, help=help_text)
        command_parser.add_argument("query" if command_name == "search" else "requirement")
        command_parser.add_argument("--installer", choices=["auto", "pip", "pipx"], default="auto")
        if command_name == "search":
            command_parser.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    if args.command == "search":
        dump_json(search(args.query, max(1, args.limit), args.installer))
        return
    if args.command == "detail":
        dump_json(detail(args.requirement, args.installer))
        return
    if args.command == "plan":
        dump_json(plan(args.requirement, args.installer))
        return
    parser.print_help(sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
