#!/usr/bin/env python3
"""Create a search plan for alternatives to a named tool."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", help="Named tool to find alternatives for.")
    parser.add_argument("--job", default="", help="Job the alternative should solve.")
    args = parser.parse_args()

    topic = f"{args.tool} {args.job}".strip()
    dump_json({
        "mode": "find-alternatives",
        "tool": args.tool,
        "job": args.job,
        "queries": [
            f'"{args.tool}" alternative "{args.job}"'.strip(),
            f'"{args.job}" "SKILL.md"',
            f'"{args.job}" "mcpServers"',
            f'"{args.job}" "package.json" "bin"',
            f'"{args.tool}" "compare"',
        ],
        "comparisonCriteria": [
            "Capability fit",
            "Availability",
            "Install/auth complexity",
            "Safety and permission scope",
            "Maintenance",
            "Integration fit",
        ],
        "notes": [
            f"Treat {args.tool} as the baseline.",
            "Alternatives are recommendations, not automatic replacements.",
        ],
    })


if __name__ == "__main__":
    main()
