"""Markdown text helpers for DebugPro validation."""

from __future__ import annotations

import re

from debugpro_validation_rules import (
    REQUIRED_AGENT_FIELDS,
    REQUIRED_ROUTER_SECTIONS,
    REQUIRED_USE_CASES,
)


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def markdown_headings(markdown: str) -> set[str]:
    matches = re.finditer(r"^#{1,6}\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
    return {normalize_text(match.group(1)) for match in matches}


def missing_router_sections(markdown: str) -> list[str]:
    headings = markdown_headings(markdown)
    return [section for section in REQUIRED_ROUTER_SECTIONS if normalize_text(section) not in headings]


def _contains_phrase_group(normalized_document: str, group) -> bool:
    return all(normalize_text(phrase) in normalized_document for phrase in group)


def missing_use_cases(markdown: str) -> list[str]:
    normalized_document = normalize_text(markdown)
    return [
        use_case
        for use_case, accepted_groups in REQUIRED_USE_CASES.items()
        if not any(_contains_phrase_group(normalized_document, group) for group in accepted_groups)
    ]


def missing_agent_fields(markdown: str) -> list[str]:
    return [field for field in REQUIRED_AGENT_FIELDS if field not in markdown]
