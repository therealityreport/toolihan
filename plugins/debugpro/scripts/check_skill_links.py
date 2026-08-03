#!/usr/bin/env python3
"""Check local links and local path references in DebugPro markdown files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from debugpro_link_check import check_links, format_issues
from debugpro_link_types import LinkIssue


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check DebugPro markdown links.")
    parser.add_argument("--root", type=Path, default=PLUGIN_ROOT, help="DebugPro plugin root.")
    parser.add_argument("--json", action="store_true", help="Print issues as JSON.")
    args = parser.parse_args(argv)

    issues = check_links(args.root)
    if args.json:
        print(json.dumps([issue.to_dict() for issue in issues], indent=2, sort_keys=True))
    else:
        print(format_issues(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
