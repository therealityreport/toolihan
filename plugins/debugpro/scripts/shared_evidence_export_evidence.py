from __future__ import annotations

from typing import Any

try:
    from .shared_evidence_export_values import coalesce, string_value
except ImportError:
    from shared_evidence_export_values import coalesce, string_value


VALID_KINDS = {"file", "command", "log", "test", "runtime", "screenshot", "url", "note"}


def normalize_evidence(value: Any, claim: str, finding: dict[str, Any]) -> list[dict[str, Any]]:
    items = value if isinstance(value, list) else []
    if not items:
        items = [fallback_evidence(claim, finding)]
    return [clean_evidence(normalize_evidence_item(item, claim)) for item in items]


def clean_evidence(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if value not in (None, "")}


def fallback_evidence(claim: str, finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "note",
        "summary": claim,
        "path": finding.get("path"),
        "line": finding.get("line"),
    }


def normalize_evidence_item(item: Any, claim: str) -> dict[str, Any]:
    evidence = item if isinstance(item, dict) else {"kind": "note", "summary": str(item)}
    return {
        "kind": normalize_evidence_kind(evidence),
        "summary": string_value(coalesce(evidence, "summary", "message", "detail"), claim),
        "path": evidence.get("path"),
        "line": positive_int_or_none(evidence.get("line")),
        "command": evidence.get("command"),
        "redacted": evidence.get("redacted") is not False,
    }


def normalize_evidence_kind(item: dict[str, Any]) -> str:
    if item.get("kind") in VALID_KINDS:
        return item["kind"]
    if item.get("command"):
        return "command"
    if item.get("path"):
        return "file"
    return "note"


def positive_int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and value > 0 else None
