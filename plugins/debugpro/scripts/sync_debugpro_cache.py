#!/usr/bin/env python3
"""Sync DebugPro source into the local Codex cache and optional mirrors."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

try:
    from .debugpro_sync_config import PLUGIN_ROOT, SyncError
    from .debugpro_sync_files import maybe_refresh_local_link, path_strings, sync_tree
    from .debugpro_sync_plan import build_plan
except ImportError:
    from debugpro_sync_config import PLUGIN_ROOT, SyncError
    from debugpro_sync_files import maybe_refresh_local_link, path_strings, sync_tree
    from debugpro_sync_plan import build_plan


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PLUGIN_ROOT, help="DebugPro source root.")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=None,
        help="Versioned cache destination.",
    )
    parser.add_argument(
        "--mirror-root",
        type=Path,
        action="append",
        default=[],
        help="Versioned mirror destination. Repeat as needed.",
    )
    parser.add_argument("--skip-local-link", action="store_true", help="Do not refresh the cache/local symlink.")
    parser.add_argument("--apply", action="store_true", help="Write the sync.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        plan = build_plan(args)
        print(json.dumps(plan, indent=2, sort_keys=True))
        if not args.apply:
            print("Dry run only. Re-run with --apply to sync DebugPro.")
            return 0

        source = Path(plan["source"])
        destinations = [Path(plan["cacheDir"]), *(Path(path) for path in plan["mirrorDirs"])]
        for destination in destinations:
            sync_tree(source, destination)
        local_link = maybe_refresh_local_link(
            Path(plan["cacheDir"]),
            apply=args.apply,
            skip=args.skip_local_link,
        )
        print(
            json.dumps(
                {
                    "status": "synced",
                    "destinations": path_strings(destinations),
                    "localLink": None if local_link is None else str(local_link),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except SyncError as exc:
        print(f"sync-debugpro-cache: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
