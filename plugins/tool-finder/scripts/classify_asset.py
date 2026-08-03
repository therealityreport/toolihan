#!/usr/bin/env python3
"""Classify a file or path into a Tool Finder asset type."""

from __future__ import annotations

import argparse
from pathlib import Path

from tool_finder_common import classify_path, dump_json, read_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="File path to classify.")
    parser.add_argument("--read", action="store_true", help="Read file contents for extra signals.")
    args = parser.parse_args()

    path = Path(args.path)
    content = read_text(path) if args.read and path.is_file() else ""
    dump_json({"path": str(path), "assetType": classify_path(str(path), content)})


if __name__ == "__main__":
    main()
