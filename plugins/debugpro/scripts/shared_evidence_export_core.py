from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from .shared_evidence_export_evidence import normalize_evidence
    from .shared_evidence_export_values import (
        coalesce,
        normalize_id,
        normalize_severity,
        normalize_status,
        string_value,
        unique_strings,
    )
except ImportError:
    from shared_evidence_export_evidence import normalize_evidence
    from shared_evidence_export_values import (
        coalesce,
        normalize_id,
        normalize_severity,
        normalize_status,
        string_value,
        unique_strings,
    )


FINDING_KEYS = ("findings", "issues", "hypotheses", "rootCauses")


def export_shared_evidence(payload: Any, *, run_id: str | None = None) -> list[dict[str, Any]]:
    findings = normalize_findings(payload)
    resolved_run_id = explicit_run_id(payload, run_id)
    return [normalize_finding(item, index, resolved_run_id) for index, item in enumerate(findings)]


def explicit_run_id(payload: Any, run_id: str | None) -> str:
    value = run_id
    if value is None and isinstance(payload, dict):
        value = payload.get("runId")
    return str(value) if value else f"debugpro-{datetime.now(timezone.utc).isoformat()}"


def normalize_findings(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in FINDING_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("Input must be a list or an object with a supported findings list.")


def normalize_finding(finding: dict[str, Any], index: int, run_id: str) -> dict[str, Any]:
    claim = finding_claim(finding, index)
    evidence = normalize_evidence(finding.get("evidence"), claim, finding)
    return {
        "runId": run_id,
        "sourcePlugin": "debugpro",
        "findingId": finding_id(finding, index),
        "severity": finding_severity(finding),
        "claim": claim,
        "evidence": evidence,
        "affectedFiles": finding_affected_files(finding, evidence),
        "recommendedNextStep": finding_next_step(finding),
        "status": normalize_status(finding.get("status")),
    }


def finding_claim(finding: dict[str, Any], index: int) -> str:
    return string_value(coalesce(finding, "claim", "title", "summary", "message"), f"Finding {index + 1}")


def finding_id(finding: dict[str, Any], index: int) -> str:
    return normalize_id(coalesce(finding, "findingId", "id") or f"DBG-{index + 1:03d}")


def finding_severity(finding: dict[str, Any]) -> str:
    return normalize_severity(coalesce(finding, "severity", "priority", "level"))


def finding_affected_files(finding: dict[str, Any], evidence: list[dict[str, Any]]) -> list[str]:
    values = coalesce(finding, "affectedFiles", "files")
    return unique_strings(values if values else evidence_paths(evidence))


def evidence_paths(evidence: list[dict[str, Any]]) -> list[Any]:
    return [item.get("path") for item in evidence if item.get("path")]


def finding_next_step(finding: dict[str, Any]) -> str:
    value = coalesce(finding, "recommendedNextStep", "nextStep", "recommendation")
    return string_value(value, "Use this evidence in the next debugging pass.")
