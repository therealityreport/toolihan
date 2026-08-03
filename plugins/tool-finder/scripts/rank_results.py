#!/usr/bin/env python3
"""Rank normalized Tool Finder results."""

from __future__ import annotations

import argparse

from tool_finder_common import add_input_arg, dump_json, final_rank_results, load_payload, result_list


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_input_arg(parser)
    args = parser.parse_args()

    ranked = final_rank_results(result_list(load_payload(args.input)))
    dump_json({"results": ranked})


if __name__ == "__main__":
    main()
