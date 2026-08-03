#!/usr/bin/env python3
"""Compare normalized Tool Finder candidates."""

from __future__ import annotations

import argparse

from tool_finder_common import add_input_arg, dump_json, load_payload, result_list, score_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_input_arg(parser)
    args = parser.parse_args()

    items = [score_result(item) for item in result_list(load_payload(args.input))]
    items.sort(key=lambda item: item.get("score", 0), reverse=True)
    best = items[0] if items else None
    callable_now = next((item for item in items if item.get("source") == "runtime"), None)
    installed = next((item for item in items if item.get("install", {}).get("status") == "installed"), None)
    installable = next((item for item in items if item.get("install", {}).get("status") == "installable"), None)
    dump_json({
        "bestOverall": best,
        "bestCallableNow": callable_now,
        "bestInstalledLocal": installed,
        "bestInstallable": installable,
        "candidateCount": len(items),
        "results": items,
    })


if __name__ == "__main__":
    main()
