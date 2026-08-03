"""Markdown target extraction for DebugPro link checking."""

from __future__ import annotations

import re
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
LOCAL_PATH_RE = re.compile(
    r"(?<![\w./-])(?:\.\./|\./)?(?:skills|agents|hooks|scripts|references)"
    r"(?:/[A-Za-z0-9._~+-]+)+"
)
SKIP_DIRS = {".git", ".codex-plugin", "__pycache__", "tests", "scripts"}


def markdown_files(root: Path) -> list[Path]:
    paths = root.rglob("*.md")
    return sorted(path for path in paths if not any(part in SKIP_DIRS for part in path.relative_to(root).parts))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_targets(text: str) -> list[tuple[str, int]]:
    link_targets = [
        (match.group(1).strip(), line_number(text, match.start()))
        for match in MARKDOWN_LINK_RE.finditer(text)
    ]
    path_targets = [
        (match.group(0).strip(), line_number(text, match.start()))
        for match in LOCAL_PATH_RE.finditer(text)
    ]
    return link_targets + path_targets
