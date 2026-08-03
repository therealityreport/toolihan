#!/usr/bin/env python3
"""Scan local paths for skills, plugins, MCP configs, hooks, CLIs, and agent files."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from tool_finder_common import classify_path, dump_json, normalize_result, read_text


DEFAULT_RELATIVE_MARKERS = {
    "SKILL.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".mcp.json",
    ".codex-plugin/plugin.json",
    "package.json",
    "pyproject.toml",
}

DEFAULT_DIR_NAMES = {"hooks", "scripts", "skills"}


def should_inspect(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if rel in DEFAULT_RELATIVE_MARKERS:
        return True
    if rel.endswith("/SKILL.md"):
        return True
    if rel.startswith(".cursor/rules/"):
        return True
    if any(part in DEFAULT_DIR_NAMES for part in rel.split("/")[:-1]):
        return path.is_file() and path.stat().st_size < 500_000
    return False


def scan_root(root: Path) -> list[dict]:
    results: list[dict] = []
    if not root.exists():
        return results

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".venv", "__pycache__"}]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            try:
                if not should_inspect(path, root):
                    continue
            except OSError:
                continue

            rel = path.relative_to(root).as_posix()
            content = read_text(path)
            asset_type = classify_path(rel, content)
            name = path.parent.name if filename == "SKILL.md" else filename
            reasons = [f"Matched local {asset_type} signal at {rel}."]
            results.append(
                normalize_result(
                    name=name,
                    asset_type=asset_type,
                    source="local",
                    path=rel,
                    local_path=str(path),
                    status="installed",
                    action="improve-local" if asset_type in {"skill", "plugin", "agent", "mcp"} else "reference-only",
                    reasons=reasons,
                    ownership="workspace-owned" if root == Path.cwd() else "local-user-owned",
                )
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="*", help="Roots to scan. Defaults to current workspace.")
    args = parser.parse_args()

    roots = [Path(p).expanduser().resolve() for p in args.roots] or [Path.cwd()]
    results: list[dict] = []
    for root in roots:
        results.extend(scan_root(root))
    dump_json({"results": results})


if __name__ == "__main__":
    main()
