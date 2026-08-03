"""Inventory helpers for DebugPro context collection."""

from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from debugpro_context_commands import run_command, safe_environment


MARKER_FILES = (
    "package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock",
    "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod",
    "pom.xml", "build.gradle", "Gemfile", "Makefile", "README.md",
)


def visible_files(root: Path, max_files: int) -> list[str]:
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if len(files) >= max_files:
            break
        parts = path.relative_to(root).parts
        if path.is_file() and not any(part.startswith(".git") for part in parts):
            files.append(str(path.relative_to(root)))
    return files


def project_inventory(root: Path, max_files: int) -> dict[str, object]:
    files = visible_files(root, max_files)
    return {
        "marker_files": [name for name in MARKER_FILES if (root / name).exists()],
        "sample_files": files,
        "sample_file_limit": max_files,
        "sample_truncated": len(files) >= max_files,
    }


def collect_context(root: Path, max_files: int) -> dict[str, object]:
    root = root.resolve()
    commands = {
        "git_status": run_command(("git", "status", "--short", "--branch"), root),
        "git_recent_commits": run_command(("git", "log", "--oneline", "-5"), root),
        "git_remotes": run_command(("git", "remote", "-v"), root),
    }
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "system": {"platform": platform.platform(), "python": sys.version.split()[0]},
        "environment": safe_environment(),
        "inventory": project_inventory(root, max_files),
        "commands": commands,
    }
