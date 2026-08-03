from __future__ import annotations

import re
from typing import Any


FIELD_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


def validate_required_fields(document: dict[str, Any], required: list[str], errors: list[str]) -> None:
    for field in required:
        if field not in document:
            errors.append(f"missing required field: {field}")


def validate_unexpected_fields(
    document: dict[str, Any],
    properties: dict[str, Any],
    errors: list[str],
) -> None:
    for field in document:
        if field not in properties:
            errors.append(f"unexpected field: {field}")


def validate_top_level_fields(
    document: dict[str, Any],
    properties: dict[str, Any],
    errors: list[str],
) -> None:
    require_non_empty_string(document, "runId", errors)
    require_enum(document, "sourcePlugin", properties["sourcePlugin"]["enum"], errors)
    validate_finding_id(document.get("findingId"), errors)
    require_enum(document, "severity", properties["severity"]["enum"], errors)
    require_non_empty_string(document, "claim", errors)
    require_non_empty_string(document, "recommendedNextStep", errors)
    require_enum(document, "status", properties["status"]["enum"], errors)


def validate_finding_id(value: Any, errors: list[str]) -> None:
    if not isinstance(value, str) or not FIELD_RE.match(value):
        errors.append("findingId has invalid format")


def require_non_empty_string(document: dict[str, Any], field: str, errors: list[str], prefix: str = "") -> None:
    label = f"{prefix}.{field}" if prefix else field
    if not isinstance(document.get(field), str) or not document[field].strip():
        errors.append(f"{label} must be a non-empty string")


def require_enum(document: dict[str, Any], field: str, values: list[str], errors: list[str], prefix: str = "") -> None:
    label = f"{prefix}.{field}" if prefix else field
    if document.get(field) not in values:
        errors.append(f"{label} must be one of: {', '.join(values)}")
