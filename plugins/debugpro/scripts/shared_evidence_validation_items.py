from __future__ import annotations

from typing import Any

try:
    from .shared_evidence_validation_fields import require_enum, require_non_empty_string
except ImportError:
    from shared_evidence_validation_fields import require_enum, require_non_empty_string


def validate_evidence(value: Any, properties: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("evidence must be a non-empty array")
        return
    item_properties = properties["evidence"]["items"]["properties"]
    for index, item in enumerate(value):
        validate_evidence_item(item, index, item_properties, errors)


def validate_evidence_item(item: Any, index: int, properties: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"evidence[{index}] must be an object")
        return
    for field in item:
        if field not in properties:
            errors.append(f"evidence[{index}] has unexpected field: {field}")
    require_enum(item, "kind", properties["kind"]["enum"], errors, prefix=f"evidence[{index}]")
    require_non_empty_string(item, "summary", errors, prefix=f"evidence[{index}]")
    validate_evidence_line(item, index, errors)
    validate_evidence_redaction(item, index, errors)


def validate_evidence_line(item: dict[str, Any], index: int, errors: list[str]) -> None:
    if "line" in item and (not isinstance(item["line"], int) or item["line"] < 1):
        errors.append(f"evidence[{index}].line must be a positive integer")


def validate_evidence_redaction(item: dict[str, Any], index: int, errors: list[str]) -> None:
    if "redacted" in item and not isinstance(item["redacted"], bool):
        errors.append(f"evidence[{index}].redacted must be boolean")


def validate_affected_files(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("affectedFiles must be an array")
        return
    if len(set(value)) != len(value):
        errors.append("affectedFiles must not contain duplicates")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append(f"affectedFiles[{index}] must be a string")
