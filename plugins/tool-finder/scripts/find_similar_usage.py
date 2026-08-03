#!/usr/bin/env python3
"""Create GitHub query plans for repositories using a tool similarly."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", help="Tool name to find usage examples for.")
    parser.add_argument("--use-case", default="", help="Desired use case.")
    args = parser.parse_args()

    use_case = args.use_case
    dump_json({
        "mode": "find-similar-usage",
        "tool": args.tool,
        "useCase": use_case,
        "queries": [
            f'"{args.tool}" ".mcp.json" "{use_case}"'.strip(),
            f'"{args.tool}" "mcpServers" "{use_case}"'.strip(),
            f'"{args.tool}" "AGENTS.md" "{use_case}"'.strip(),
            f'"{args.tool}" "SKILL.md" "{use_case}"'.strip(),
            f'"{args.tool}" "package.json" "{use_case}"'.strip(),
            f'"{args.tool}" "pyproject.toml" "{use_case}"'.strip(),
        ],
        "evidencePreference": [
            "Config files",
            "Imports",
            "Command invocations",
            "MCP setup",
            "Plugin manifests",
            "Skill files",
            "Agent instruction files",
        ],
        "notes": [
            "Prefer code/config hits over README-only mentions.",
            "Similar repos are evidence, not install recommendations.",
        ],
    })


if __name__ == "__main__":
    main()
