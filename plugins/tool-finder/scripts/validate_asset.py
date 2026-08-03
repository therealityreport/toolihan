#!/usr/bin/env python3
"""Validate basic Tool Finder asset shapes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tool_finder_common import classify_path, dump_json, read_text


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def validate_skill(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    match = FRONTMATTER_RE.match(text)
    if not match:
        return ["Missing YAML-style frontmatter."]
    body = match.group("body")
    if "name:" not in body:
        issues.append("Frontmatter missing name.")
    if "description:" not in body:
        issues.append("Frontmatter missing description.")
    return issues


def validate_json(path: Path) -> list[str]:
    try:
        json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON: {exc}"]
    return []


def validate_plugin_manifest(path: Path) -> list[str]:
    issues = validate_json(path)
    if issues:
        return issues
    payload = json.loads(read_text(path))
    for field in ("name", "version", "description", "skills", "interface"):
        if field not in payload:
            issues.append(f"Missing plugin manifest field: {field}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Asset files to validate.")
    args = parser.parse_args()

    results = []
    for raw in args.paths:
        path = Path(raw)
        text = read_text(path)
        asset_type = classify_path(str(path), text)
        issues: list[str] = []
        if asset_type == "skill":
            issues = validate_skill(path, text)
        elif asset_type == "plugin":
            issues = validate_plugin_manifest(path)
        elif asset_type == "mcp" or path.suffix == ".json":
            issues = validate_json(path)
        results.append({
            "path": str(path),
            "assetType": asset_type,
            "valid": not issues,
            "issues": issues,
        })
    dump_json({"results": results})


if __name__ == "__main__":
    main()
