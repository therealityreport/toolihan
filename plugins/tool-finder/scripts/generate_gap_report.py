#!/usr/bin/env python3
"""Generate a simple gap report for a selected Tool Finder result."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json, load_payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Selected result JSON file, or '-' for stdin.")
    parser.add_argument("--goal", required=True, help="User goal for the tool.")
    args = parser.parse_args()

    item = load_payload(args.input)
    gaps: list[str] = []
    if item.get("assetType") == "unknown":
        gaps.append("Asset type is unknown.")
    if not item.get("reasons"):
        gaps.append("No concrete match reasons are recorded.")
    if item.get("safety", {}).get("status") in {None, "unknown"}:
        gaps.append("Safety/audit status is unknown.")
    if not item.get("install", {}).get("command") and not item.get("install", {}).get("installUrl"):
        gaps.append("No install or use path is recorded.")
    if item.get("maintenance", {}).get("isDuplicate"):
        gaps.append("Candidate is marked as duplicate.")

    dump_json({
        "name": item.get("name"),
        "goal": args.goal,
        "recommendedAction": item.get("recommendedAction", "reference-only"),
        "gaps": gaps,
        "patchPlan": [
            "Tighten description and trigger language.",
            "Add missing examples or templates only when they directly support the goal.",
            "Add validation commands for any generated asset.",
        ],
    })


if __name__ == "__main__":
    main()
