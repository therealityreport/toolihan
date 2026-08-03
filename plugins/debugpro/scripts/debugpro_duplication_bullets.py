from __future__ import annotations

import re
from pathlib import Path

try:
    from .debugpro_duplication_refs import SHARED_REFERENCES, read_text
    from .debugpro_duplication_types import DuplicationIssue
except ImportError:
    from debugpro_duplication_refs import SHARED_REFERENCES, read_text
    from debugpro_duplication_types import DuplicationIssue


LONG_BULLET_MIN_CHARS = 52
MAX_SHARED_BULLET_FILES = 2


def markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def normalize_bullet(line: str) -> str:
    line = re.sub(r"^\s*[-*]\s+", "", line).strip().lower()
    line = re.sub(r"`([^`]+)`", r"\1", line)
    line = re.sub(r"\s+", " ", line)
    return line.rstrip(".")


def should_scan_bullets(root: Path, path: Path) -> Path | None:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    if relative in SHARED_REFERENCES:
        return None
    return relative if str(relative).startswith("skills/") else None


def long_bullets(path: Path) -> list[str]:
    bullets: list[str] = []
    for line in read_text(path).splitlines():
        if not re.match(r"^\s*[-*]\s+", line):
            continue
        normalized = normalize_bullet(line)
        if len(normalized) >= LONG_BULLET_MIN_CHARS:
            bullets.append(normalized)
    return bullets


def repeated_bullet_issue(bullet: str, paths: list[Path]) -> DuplicationIssue | None:
    unique_paths = sorted(set(paths), key=str)
    if len(unique_paths) <= MAX_SHARED_BULLET_FILES:
        return None
    joined_paths = ", ".join(str(path) for path in unique_paths)
    return DuplicationIssue("repeated_long_bullet", joined_paths, f"Repeated bullet needs a shared reference: {bullet}")


def repeated_long_bullets(root: Path) -> list[DuplicationIssue]:
    occurrences = bullet_occurrences(root)
    issues: list[DuplicationIssue] = []
    for bullet, paths in sorted(occurrences.items()):
        issue = repeated_bullet_issue(bullet, paths)
        if issue is not None:
            issues.append(issue)
    return issues


def bullet_occurrences(root: Path) -> dict[str, list[Path]]:
    occurrences: dict[str, list[Path]] = {}
    for path in markdown_files(root):
        relative = should_scan_bullets(root, path)
        if relative is None:
            continue
        add_bullets(occurrences, relative, path)
    return occurrences


def add_bullets(occurrences: dict[str, list[Path]], relative: Path, path: Path) -> None:
    for bullet in long_bullets(path):
        occurrences.setdefault(bullet, []).append(relative)
