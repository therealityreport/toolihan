from __future__ import annotations

from typing import Any

try:
    from .shared_evidence_validation_fields import (
        validate_required_fields,
        validate_top_level_fields,
        validate_unexpected_fields,
    )
    from .shared_evidence_validation_items import validate_affected_files, validate_evidence
    from .shared_evidence_validation_schema import SCHEMA_PATH, load_json
except ImportError:
    from shared_evidence_validation_fields import (
        validate_required_fields,
        validate_top_level_fields,
        validate_unexpected_fields,
    )
    from shared_evidence_validation_items import validate_affected_files, validate_evidence
    from shared_evidence_validation_schema import SCHEMA_PATH, load_json


def validate(document: Any, schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_json(SCHEMA_PATH)
    if not isinstance(document, dict):
        return ["document must be an object"]

    errors: list[str] = []
    properties = schema["properties"]
    validate_required_fields(document, schema["required"], errors)
    validate_unexpected_fields(document, properties, errors)
    validate_top_level_fields(document, properties, errors)
    validate_evidence(document.get("evidence"), properties, errors)
    validate_affected_files(document.get("affectedFiles"), errors)
    return errors
