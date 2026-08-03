"""Manifest and README checks for DebugPro validation."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

from debugpro_validation_text import normalize_text, read_text


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
ALLOWED_TOP_FIELDS = {
    "name", "version", "description", "author", "homepage", "repository",
    "license", "keywords", "skills", "interface",
}
ALLOWED_INTERFACE_FIELDS = {
    "displayName", "shortDescription", "longDescription", "developerName",
    "category", "capabilities", "websiteURL", "privacyPolicyURL",
    "termsOfServiceURL", "defaultPrompt", "default_prompt", "brandColor",
}
REQUIRED_INTERFACE_FIELDS = (
    "displayName", "shortDescription", "longDescription", "developerName", "category",
)


def load_json(path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(read_text(path)), None
    except FileNotFoundError:
        return None, "file is missing"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def manifest_schema_issues(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest root must be an object"]
    issues = []
    for field in (
        "name", "version", "description", "author", "homepage", "repository",
        "license", "keywords", "skills", "interface",
    ):
        if not manifest.get(field):
            issues.append(f"missing required field {field}")
    for field in sorted(set(manifest) - ALLOWED_TOP_FIELDS):
        issues.append(f"unsupported top-level field {field}")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        issues.append("version must use strict semver")
    if manifest.get("name") != "debugpro":
        issues.append("name must be debugpro")
    if manifest.get("skills") != "./skills/":
        issues.append("skills must be ./skills/")
    author = manifest.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
        issues.append("author.name must be a non-empty string")
    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) and item for item in keywords):
        issues.append("keywords must be a non-empty string array")
    for field in ("homepage", "repository"):
        value = manifest.get(field)
        if not _is_https_url(value):
            issues.append(f"{field} must be an absolute https URL")
    interface = manifest.get("interface")
    if isinstance(interface, dict):
        for field in sorted(set(interface) - ALLOWED_INTERFACE_FIELDS):
            issues.append(f"unsupported interface field {field}")
        for field in REQUIRED_INTERFACE_FIELDS:
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"interface.{field} must be a non-empty string")
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or not all(
            isinstance(item, str) and item for item in capabilities
        ):
            issues.append("interface.capabilities must be a non-empty string array")
        prompts = interface.get("defaultPrompt", interface.get("default_prompt"))
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or not all(
            isinstance(item, str) and 0 < len(item) <= 128 for item in prompts
        ):
            issues.append("interface.defaultPrompt must contain one to three short prompts")
        for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            value = interface.get(field)
            if value and not _is_https_url(value):
                issues.append(f"interface.{field} must be an absolute https URL")
    return issues


def _is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def readme_explains_router(markdown: str) -> bool:
    normalized = normalize_text(markdown)
    required = ("capability router", "capability routing", "skill routing")
    technique_terms = ("technique indexing", "technique index")
    return all(term in normalized for term in required) and any(term in normalized for term in technique_terms)
