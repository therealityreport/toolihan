#!/usr/bin/env python3
"""Detect repeated DebugPro boilerplate that should live in shared references."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .debugpro_duplication_bullets import repeated_long_bullets
    from .debugpro_duplication_refs import SHARED_REFERENCES, missing_reference_links, shared_references_missing
    from .debugpro_duplication_types import DuplicationIssue
except ImportError:
    from debugpro_duplication_bullets import repeated_long_bullets
    from debugpro_duplication_refs import SHARED_REFERENCES, missing_reference_links, shared_references_missing
    from debugpro_duplication_types import DuplicationIssue


def check_duplication(root: Path | str) -> list[DuplicationIssue]:
    root = Path(root).resolve()
    issues: list[DuplicationIssue] = []
    issues.extend(shared_references_missing(root))
    issues.extend(missing_reference_links(root))
    issues.extend(repeated_long_bullets(root))
    return issues


def format_issues(issues: list[DuplicationIssue]) -> str:
    if not issues:
        return "DebugPro duplication check: PASS"
    lines = ["DebugPro duplication check: FAIL"]
    lines.extend(f"- {issue.code}: {issue.path}: {issue.message}" for issue in issues)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="DebugPro plugin root")
    parser.add_argument("--json", action="store_true", help="emit JSON diagnostics")
    args = parser.parse_args()

    issues = check_duplication(args.root)
    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], indent=2))
    else:
        print(format_issues(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
