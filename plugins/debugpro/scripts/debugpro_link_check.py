"""Local link resolution used by DebugPro markdown checks."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from debugpro_link_extract import extract_targets, markdown_files
from debugpro_link_types import LinkIssue


def is_external(target: str) -> bool:
    return urlparse(target).scheme in {"http", "https", "mailto", "app"}


def strip_anchor(target: str) -> str:
    return target.split("#", 1)[0].split("?", 1)[0]


def candidate_targets(root: Path, source: Path, cleaned: str) -> list[Path]:
    candidates: list[Path] = []
    if cleaned.startswith("/"):
        candidates.append(root / cleaned.lstrip("/"))
    if cleaned.startswith(("skills/", "agents/", "hooks/", "scripts/", "tests/")):
        candidates.append(root / cleaned)
    return [*candidates, source.parent / cleaned, root / cleaned]


def resolve_target(root: Path, source: Path, target: str) -> Path | None:
    cleaned = strip_anchor(target).strip()
    if not cleaned or is_external(cleaned):
        return None

    first_candidate: Path | None = None
    for candidate in candidate_targets(root, source, cleaned):
        normalized = candidate.resolve()
        first_candidate = first_candidate or normalized
        try:
            normalized.relative_to(root)
        except ValueError:
            continue
        if normalized.exists():
            return normalized
    return first_candidate


def check_links(root: Path | str) -> list[LinkIssue]:
    root = Path(root).resolve()
    issues: list[LinkIssue] = []
    for source in markdown_files(root):
        text = source.read_text(encoding="utf-8", errors="replace")
        for target, line in extract_targets(text):
            cleaned = strip_anchor(target)
            resolved = resolve_target(root, source, target)
            if cleaned and not is_external(cleaned) and (resolved is None or not resolved.exists()):
                issues.append(
                    LinkIssue(
                        str(source.relative_to(root)),
                        target,
                        line,
                        "local link target does not exist",
                    )
                )
    return issues


def format_issues(issues: Sequence[LinkIssue]) -> str:
    if not issues:
        return "DebugPro link check: PASS"
    lines = ["DebugPro link check: FAIL"]
    lines.extend(f"- {issue.source}:{issue.line}: {issue.target} ({issue.message})" for issue in issues)
    return "\n".join(lines)
