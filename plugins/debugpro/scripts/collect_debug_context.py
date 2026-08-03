#!/usr/bin/env python3
"""Collect compact local context for a DebugPro handoff.

This compatibility entrypoint accepts both the newer positional root form and
the planned `--repo` spelling.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from debugpro_context_inventory import collect_context


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect compact local debugging context.")
    parser.add_argument("root", nargs="?", type=Path, help="Project root.")
    parser.add_argument("--repo", type=Path, help="Project root alias for compatibility.")
    parser.add_argument("--max-files", type=int, default=200, help="Maximum file paths to sample.")
    args = parser.parse_args(argv)

    root = args.repo or args.root or Path.cwd()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2
    print(json.dumps(collect_context(root, args.max_files), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
