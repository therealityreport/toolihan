from __future__ import annotations

import re
from typing import Any


VALID_SEVERITIES = {"blocker", "critical", "high", "medium", "low", "info"}
VALID_STATUSES = {"open", "accepted", "deferred", "resolved", "rejected"}
SEVERITY_ALIASES = {"p0": "critical", "p1": "high", "p2": "medium", "p3": "low"}


def coalesce(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value:
            return value
    return None


def normalize_severity(value: Any) -> str:
    normalized = str(value or "info").lower()
    if normalized in VALID_SEVERITIES:
        return normalized
    return SEVERITY_ALIASES.get(normalized, "info")


def normalize_status(value: Any) -> str:
    normalized = str(value or "open").lower()
    return normalized if normalized in VALID_STATUSES else "open"


def normalize_id(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", str(value or "finding")).strip("-") or "finding"


def unique_strings(values: Any) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    if not isinstance(values, list):
        return output
    for value in values:
        normalized = value.strip() if isinstance(value, str) else ""
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(normalized)
    return output


def string_value(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback
