#!/usr/bin/env python3
"""Create a dry-run install or wiring plan for a normalized result."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json, load_payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Normalized result JSON file, or '-' for stdin.")
    args = parser.parse_args()

    item = load_payload(args.input)
    install = item.get("install", {})
    command = install.get("command") or install.get("installUrl")
    dump_json({
        "mode": "dry-run-install-plan",
        "name": item.get("name"),
        "assetType": item.get("assetType"),
        "source": item.get("source"),
        "willExecute": False,
        "executionDesign": "docs/confirmed-install-execution.md",
        "commandOrUrl": command,
        "requiresAuth": install.get("requiresAuth", False),
        "filesThatMayChange": [],
        "rollbackNotes": [
            "No changes are made by this planner.",
            "Confirmed install execution requires a separate user decision and rollback design.",
        ],
        "risks": item.get("safety", {}).get("notes", []),
    })


if __name__ == "__main__":
    main()
