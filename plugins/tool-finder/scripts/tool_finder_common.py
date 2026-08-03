#!/usr/bin/env python3
"""Shared helpers for Tool Finder scripts."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


LIVE_PROVIDER_SOURCES = {"github", "hugging-face", "npm", "pypi", "homebrew", "pips", "python", "skills.sh"}
PACKAGE_REGISTRY_SOURCES = {"npm", "pypi", "homebrew", "pips", "python"}
CONNECTOR_PLUGIN_SOURCES = {"github-connector", "hugging-face-connector"}

ASSET_TYPE_PATTERNS = (
    ("skill", re.compile(r"(^|/)SKILL\.md$", re.IGNORECASE)),
    ("plugin", re.compile(r"(^|/)\.codex-plugin/plugin\.json$", re.IGNORECASE)),
    ("mcp", re.compile(r"(^|/)\.mcp\.json$", re.IGNORECASE)),
    ("agent", re.compile(r"(^|/)(AGENTS|CLAUDE|GEMINI)\.md$", re.IGNORECASE)),
    ("agent", re.compile(r"(^|/)\.cursor/rules/", re.IGNORECASE)),
    ("hook", re.compile(r"(^|/)hooks?/", re.IGNORECASE)),
    ("cli", re.compile(r"(^|/)(package\.json|pyproject\.toml)$", re.IGNORECASE)),
    ("script", re.compile(r"(^|/)scripts?/", re.IGNORECASE)),
)


def read_text(path: Path, max_bytes: int = 250_000) -> str:
    try:
        with path.open("rb") as handle:
            return handle.read(max_bytes).decode("utf-8", errors="replace")
    except OSError:
        return ""


def classify_path(path: str, content: str = "") -> str:
    normalized = path.replace(os.sep, "/")
    for asset_type, pattern in ASSET_TYPE_PATTERNS:
        if pattern.search(normalized):
            return asset_type

    lower_content = content.lower()
    if "mcpservers" in lower_content or "modelcontextprotocol" in lower_content:
        return "mcp"
    if "console_scripts" in lower_content or '"bin"' in lower_content:
        return "cli"
    if "name:" in lower_content and "description:" in lower_content and "skill" in lower_content:
        return "skill"
    return "unknown"


def stable_id(source: str, path: str) -> str:
    return f"{source}:{path}"


def provider_status(
    provider: str,
    *,
    state: str,
    searched: bool,
    skipped: bool = False,
    reason: str | None = None,
    remediation: list[str] | None = None,
    requires_auth: bool = False,
    variant: str | None = None,
    result_count: int | None = None,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "variant": variant,
        "state": state,
        "searched": searched,
        "skipped": skipped,
        "requiresAuth": requires_auth,
        "reason": reason,
        "remediation": remediation or [],
        "resultCount": result_count,
    }


def default_provider_status(source: str) -> dict[str, Any]:
    if source == "runtime":
        return provider_status("runtime", state="available", searched=True, reason="Callable in the current Codex session.")
    if source == "local":
        return provider_status("local", state="available", searched=True, reason="Found in local filesystem inventory.")
    if source in LIVE_PROVIDER_SOURCES:
        return provider_status(source, state="queried", searched=True, reason="Live provider lookup was executed.")
    return provider_status(source, state="unknown", searched=False, reason="Provider status was not supplied.")


def default_provider_source(source: str) -> str:
    if source == "runtime":
        return "runtime-catalog"
    if source == "local":
        return "local-filesystem"
    if source in CONNECTOR_PLUGIN_SOURCES:
        return "connector-plugin"
    if source in PACKAGE_REGISTRY_SOURCES:
        return "package-registry"
    if source in {"github", "hugging-face", "skills.sh"}:
        return "direct-api"
    return "unknown"


def normalize_result(
    *,
    name: str,
    asset_type: str,
    source: str,
    path: str | None = None,
    local_path: str | None = None,
    url: str | None = None,
    repo: str | None = None,
    status: str = "unknown",
    action: str = "reference-only",
    reasons: list[str] | None = None,
    risks: list[str] | None = None,
    install_command: str | None = None,
    install_url: str | None = None,
    source_trust: str = "unknown",
    ownership: str = "unknown",
    external_ids: dict[str, Any] | None = None,
    safety: dict[str, Any] | None = None,
    maintenance: dict[str, Any] | None = None,
    api_evidence: dict[str, Any] | None = None,
    provider_status: dict[str, Any] | None = None,
    provider_source: str | None = None,
) -> dict[str, Any]:
    item_path = path or local_path or url or name
    return {
        "id": stable_id(source, item_path),
        "name": name,
        "assetType": asset_type,
        "source": source,
        "providerSource": provider_source or default_provider_source(source),
        "sourceTrust": source_trust,
        "ownership": ownership,
        "externalIds": {
            "skillsShId": None,
            "sourceType": None,
            "contentHash": None,
            **(external_ids or {}),
        },
        "location": {
            "url": url,
            "repo": repo,
            "path": path,
            "localPath": local_path,
        },
        "capabilities": [],
        "install": {
            "status": status,
            "command": install_command,
            "requiresAuth": False,
            "installUrl": install_url,
        },
        "safety": {
            "status": "unknown",
            "riskLevel": "unknown",
            "notes": risks or [],
            **(safety or {}),
        },
        "maintenance": {
            "lastUpdated": None,
            "isArchived": False,
            "installs": None,
            "isDuplicate": False,
            "signals": [],
            **(maintenance or {}),
        },
        "apiEvidence": {
            "searchType": "unknown",
            "rateLimitRemaining": None,
            "cacheUntil": None,
            **(api_evidence or {}),
        },
        "providerStatus": provider_status or default_provider_status(source),
        "usageExamples": [],
        "alternatives": [],
        "score": 0,
        "bucket": "reference",
        "recommendedAction": action,
        "reasons": reasons or [],
        "penalties": [],
        "rejectionReason": None,
    }


def load_payload(path: str | None = None) -> Any:
    if path and path != "-":
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def dump_json(payload: Any) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def result_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise SystemExit("Expected a JSON list or an object with a results array.")


def signal_int(result: dict[str, Any], prefix: str) -> int | None:
    for signal in result.get("maintenance", {}).get("signals") or []:
        text = str(signal)
        if not text.startswith(prefix):
            continue
        value = text[len(prefix):]
        if value.isdigit():
            return int(value)
    return None


def signal_bool(result: dict[str, Any], prefix: str) -> bool | None:
    for signal in result.get("maintenance", {}).get("signals") or []:
        text = str(signal)
        if text.startswith(prefix):
            return text[len(prefix):].lower() == "true"
    return None


def has_capability_prefix(result: dict[str, Any], prefix: str) -> bool:
    return any(str(capability).startswith(prefix) for capability in result.get("capabilities") or [])


def score_result(result: dict[str, Any]) -> dict[str, Any]:
    score = 0
    reasons = list(result.get("reasons") or [])
    penalties = list(result.get("penalties") or [])

    if result.get("assetType") and result["assetType"] != "unknown":
        score += 10
    if result.get("source") == "runtime":
        score += 20
        reasons.append("Callable in the current Codex session.")
    if result.get("source") == "local":
        score += 15
        reasons.append("Already present in local inventory.")
    if result.get("source") == "skills.sh":
        score += 10
        reasons.append("Discovered through structured skills.sh metadata.")
    if result.get("source") in {"github", "npm", "pypi", "homebrew", "pips", "python"}:
        score += 10
        reasons.append("Discovered through a live provider lookup.")
    if result.get("source") == "hugging-face":
        score += 10
        reasons.append("Discovered through a live Hugging Face provider lookup.")
    if result.get("providerSource") == "connector-plugin":
        score += 15
        reasons.append("Discovered through a callable plugin connector catalog.")
    if result.get("sourceTrust") in {"first-party", "curated", "user-owned"}:
        score += 15
    elif result.get("sourceTrust") in {"registry", "public-source"}:
        score += 10
    if result.get("install", {}).get("status") in {"already-available", "installed"}:
        score += 15
    elif result.get("install", {}).get("status") == "installable":
        score += 10
    if result.get("install", {}).get("installUrl") or result.get("install", {}).get("command"):
        score += 5
    if result.get("source") == "github" and result.get("location", {}).get("url"):
        score += 10
        reasons.append("Has a direct GitHub reference URL.")
    if result.get("source") == "hugging-face" and result.get("location", {}).get("url"):
        score += 5
        reasons.append("Has a direct Hugging Face Hub reference URL.")
    if result.get("source") == "hugging-face":
        downloads = result.get("maintenance", {}).get("installs")
        if not isinstance(downloads, int):
            downloads = signal_int(result, "downloads:")
        likes = signal_int(result, "likes:")
        if isinstance(downloads, int):
            if downloads >= 1_000_000:
                score += 20
                reasons.append("Hugging Face Hub downloads indicate very high adoption.")
            elif downloads >= 100_000:
                score += 15
                reasons.append("Hugging Face Hub downloads indicate high adoption.")
            elif downloads >= 10_000:
                score += 10
                reasons.append("Hugging Face Hub downloads indicate meaningful adoption.")
            elif downloads >= 1_000:
                score += 5
                reasons.append("Hugging Face Hub downloads indicate some adoption.")
        if isinstance(likes, int):
            if likes >= 1_000:
                score += 10
                reasons.append("Hugging Face likes indicate strong community interest.")
            elif likes >= 100:
                score += 7
                reasons.append("Hugging Face likes indicate community interest.")
            elif likes >= 10:
                score += 4
                reasons.append("Hugging Face likes provide a small positive signal.")
        if has_capability_prefix(result, "pipeline:"):
            score += 5
            reasons.append("Hugging Face result declares a task pipeline.")
        if has_capability_prefix(result, "sdk:"):
            score += 5
            reasons.append("Hugging Face result declares a Space SDK/runtime.")
        if has_capability_prefix(result, "tags:"):
            score += 3
            reasons.append("Hugging Face result includes descriptive tags.")
        if signal_bool(result, "gated:"):
            score -= 5
            penalties.append("Hugging Face resource is gated.")
        if signal_bool(result, "private:"):
            score -= 20
            penalties.append("Hugging Face resource is private.")
    if result.get("safety", {}).get("status") == "pass":
        score += 10
    if result.get("safety", {}).get("riskLevel") in {"none", "low"}:
        score += 5
    if result.get("maintenance", {}).get("lastUpdated"):
        score += 5
    if result.get("maintenance", {}).get("isArchived"):
        score -= 15
        penalties.append("Repository or package appears archived.")
    if result.get("maintenance", {}).get("isDuplicate"):
        score -= 10
        penalties.append("Marked as duplicate.")
    if result.get("rejectionReason"):
        score = min(score, 39)

    score = max(0, min(100, score))
    if score >= 80:
        bucket = "strong"
    elif score >= 60:
        bucket = "usable"
    elif score >= 40:
        bucket = "reference"
    else:
        bucket = "reject"

    result["score"] = score
    result["bucket"] = bucket
    result["reasons"] = unique(reasons)
    result["penalties"] = unique(penalties)
    if bucket == "reject" and not result.get("rejectionReason"):
        result["rejectionReason"] = "Low score after fit, trust, availability, and safety checks."
    return result


def final_rank_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rescored = [score_result(dict(item)) for item in results]
    rescored.sort(
        key=lambda item: (
            item.get("score", 0),
            item.get("providerSource") == "connector-plugin",
            item.get("source") == "runtime",
            bool((item.get("location") or {}).get("url") or (item.get("install") or {}).get("command")),
        ),
        reverse=True,
    )
    for index, item in enumerate(rescored, start=1):
        item["rank"] = index
        item["rankReason"] = (
            f"Ranked #{index} after final scoring across all providers, "
            f"dedupe, availability, provider source, safety, and maintenance signals."
        )
    return rescored


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def add_input_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", nargs="?", default="-", help="JSON input file, or stdin with '-'.")
