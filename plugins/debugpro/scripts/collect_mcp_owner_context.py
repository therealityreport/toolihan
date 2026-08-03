#!/usr/bin/env python3
"""Collect local MCP ownership and runtime context without external packages."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from debugpro_context_commands import run_command
from debugpro_redaction import config_key_names


DEFAULT_PATHS = (
    Path.home() / ".codex" / "config.toml",
    Path.home() / ".codex" / "mcp.json",
    Path.home() / ".agents" / "mcp.json",
    Path.home() / "Library/Application Support/codex-plusplus/extension-host-config.json",
)
COMMANDS = (
    ("codex", "doctor", "--json"),
    ("mcp-status", "--json", "--verbose"),
    ("chrome-control-health", "--json"),
)
def read_config_summary(path: Path, max_lines: int) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": str(path), "exists": True, "error": str(exc)}
    lines = text.splitlines()
    return {
        "path": str(path),
        "exists": True,
        "line_count": len(lines),
        "keys": config_key_names("\n".join(lines[:max_lines])),
        "preview_truncated": len(lines) > max_lines,
    }


def collect(max_lines: int, timeout: int) -> dict[str, object]:
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "CODEX_HOME": "present" if os.environ.get("CODEX_HOME") else "missing",
            "MCP_CONFIG": "present" if os.environ.get("MCP_CONFIG") else "missing",
        },
        "config_files": [read_config_summary(path, max_lines) for path in DEFAULT_PATHS],
        "commands": [run_command(command, Path.cwd(), timeout) for command in COMMANDS],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect local MCP owner context.")
    parser.add_argument("--max-lines", type=int, default=80, help="Maximum lines per config preview.")
    parser.add_argument("--timeout", type=int, default=12, help="Command timeout in seconds.")
    args = parser.parse_args(argv)

    print(json.dumps(collect(args.max_lines, args.timeout), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
