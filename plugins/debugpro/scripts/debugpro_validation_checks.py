"""Top-level DebugPro validation checks."""

from __future__ import annotations

from pathlib import Path

from debugpro_validation_manifest import (
    load_json,
    manifest_schema_issues,
    readme_explains_router,
)
from debugpro_validation_rules import MANIFESTS, README, ROOT_SKILL, ROUTER_AGENT, ROUTER_REFERENCE
from debugpro_validation_text import (
    missing_agent_fields,
    missing_router_sections,
    missing_use_cases,
    read_text,
)
from debugpro_validation_types import Diagnostic


def validate_router_reference(root: Path) -> list[Diagnostic]:
    router_path = root / ROUTER_REFERENCE
    if not router_path.exists():
        return [
            Diagnostic(
                "missing_capability_router_reference",
                str(ROUTER_REFERENCE),
                "skills/debugpro/references/capability-router.md is missing.",
            )
        ]

    router = read_text(router_path)
    diagnostics = [
        Diagnostic(
            "router_section_missing",
            str(ROUTER_REFERENCE),
            f"capability-router.md is missing the {section!r} section.",
        )
        for section in missing_router_sections(router)
    ]
    diagnostics.extend(
        Diagnostic(
            "router_use_case_missing",
            str(ROUTER_REFERENCE),
            f"capability-router.md does not cover the {use_case!r} use case.",
        )
        for use_case in missing_use_cases(router)
    )
    return diagnostics


def validate_router_agent(root: Path) -> list[Diagnostic]:
    agent_path = root / ROUTER_AGENT
    if not agent_path.exists():
        return [
            Diagnostic(
                "missing_capability_router_agent",
                str(ROUTER_AGENT),
                "agents/debugpro-capability-router.md is missing.",
            )
        ]

    agent = read_text(agent_path)
    return [
        Diagnostic(
            "router_agent_field_missing",
            str(ROUTER_AGENT),
            f"debugpro-capability-router.md is missing the output field {field!r}.",
        )
        for field in missing_agent_fields(agent)
    ]


def validate_root_skill(root: Path) -> list[Diagnostic]:
    root_skill_path = root / ROOT_SKILL
    if not root_skill_path.exists():
        return [Diagnostic("root_skill_missing", str(ROOT_SKILL), "root DebugPro skill is missing.")]
    if "capability-router.md" in read_text(root_skill_path):
        return []
    return [
        Diagnostic(
            "root_skill_router_missing",
            str(ROOT_SKILL),
            "root DebugPro skill does not mention capability-router.md.",
        )
    ]


def validate_manifests(root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for manifest_rel in MANIFESTS:
        manifest, error = load_json(root / manifest_rel)
        if error:
            diagnostics.append(Diagnostic("manifest_invalid", str(manifest_rel), f"manifest {error}."))
        else:
            diagnostics.extend(
                Diagnostic(
                    "manifest_schema_invalid",
                    str(manifest_rel),
                    issue,
                )
                for issue in manifest_schema_issues(manifest)
            )
    return diagnostics


def validate_readme(root: Path) -> list[Diagnostic]:
    readme_path = root / README
    if not readme_path.exists():
        return [Diagnostic("readme_missing", str(README), "README.md is missing.")]
    if readme_explains_router(read_text(readme_path)):
        return []
    return [
        Diagnostic(
            "readme_router_explanation_missing",
            str(README),
            "README.md does not explain capability routing, skill routing, and technique indexing.",
        )
    ]


def validate(root: Path | str) -> list[Diagnostic]:
    root = Path(root).resolve()
    diagnostics: list[Diagnostic] = []
    validators = (
        validate_router_reference,
        validate_router_agent,
        validate_root_skill,
        validate_manifests,
        validate_readme,
    )
    for validator in validators:
        diagnostics.extend(validator(root))
    return diagnostics
