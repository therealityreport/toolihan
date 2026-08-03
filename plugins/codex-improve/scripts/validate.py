#!/usr/bin/env python3
"""Validate Codex Improve packaging and universal role integration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


PLUGIN = Path(__file__).resolve().parent.parent
SKILL = PLUGIN / "skills" / "codex-improve"
REPO = PLUGIN.parent.parent
ROUTING_ROOT = Path(
    os.environ.get(
        "CODEX_IMPROVE_ROUTING_ROOT",
        Path.home() / ".codex" / "skills" / "subagent-routing",
    )
).expanduser()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict[str, object]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(parsed, dict), f"expected JSON object: {path}")
    return parsed


def validate_manifest() -> None:
    manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    marketplace_path = Path(
        os.environ.get(
            "CODEX_IMPROVE_MARKETPLACE",
            REPO / ".agents" / "plugins" / "marketplace.json",
        )
    )
    if not marketplace_path.is_file():
        marketplace_path = Path.home() / ".agents" / "plugins" / "marketplace.json"
    marketplace = load_json(marketplace_path)

    require(manifest["name"] == "codex-improve", "plugin name mismatch")
    require(manifest["version"] == "0.2.0", "plugin version must be 0.2.0")
    require(manifest["skills"] == "./skills/", "skill path mismatch")
    require("TODO" not in json.dumps(manifest), "manifest contains TODO placeholders")
    require("universal role catalog" in manifest["description"], "manifest does not describe universal routing")
    entry = next(
        (item for item in marketplace["plugins"] if item.get("name") == manifest["name"]),
        None,
    )
    require(entry is not None, f"codex-improve entry missing from {marketplace_path}")
    require(entry["name"] == manifest["name"], "marketplace name mismatch")
    require(entry["source"]["path"] == "./plugins/codex-improve", "marketplace path mismatch")
    require(
        entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "marketplace policy mismatch",
    )


def validate_universal_mapping() -> None:
    mapping_path = SKILL / "assets" / "universal-role-mappings.json"
    catalog_path = ROUTING_ROOT / "references" / "universal-role-catalog.json"
    mapping = load_json(mapping_path)
    catalog = load_json(catalog_path)

    require(mapping["schemaVersion"] == 1, "mapping schema version mismatch")
    mapping_catalog = mapping["catalog"]
    require(isinstance(mapping_catalog, dict), "mapping catalog must be an object")
    require(mapping_catalog["id"] == catalog["catalogId"], "mapping catalog id mismatch")
    require(mapping_catalog["schemaVersion"] == catalog["schemaVersion"], "mapping catalog schema mismatch")
    require(
        mapping_catalog["healthCheck"] == "skills/subagent-routing/scripts/sync-universal-roles.py --check --json",
        "mapping health check mismatch",
    )

    gate = mapping["lunaGate"]
    require(isinstance(gate, dict), "Luna gate must be an object")
    require(gate["model"] == "gpt-5.6-luna", "Luna gate model mismatch")
    require(gate["statusPath"] == "runtime.gatedModels.gpt-5.6-luna.status", "Luna gate path mismatch")
    require(gate["allowedStatuses"] == ["proven"], "Luna gate must require proof")
    require("BLOCKED" in gate["whenUnavailable"], "Luna gate must block unavailable routing")

    catalog_roles = catalog["roles"]
    require(isinstance(catalog_roles, list), "catalog roles must be a list")
    catalog_names = {role["name"] for role in catalog_roles if isinstance(role, dict)}
    legacy_mappings = mapping["legacyMappings"]
    require(isinstance(legacy_mappings, list), "legacy mappings must be a list")
    expected_legacy = {
        "Workflow lead",
        "Recon mapping",
        "Bulk audit",
        "Specialist audit",
        "Evidence and plan review",
        "Plan authoring",
        "Execution",
        "Risky execution",
        "Final critical judgment",
    }
    observed_legacy: set[str] = set()
    for item in legacy_mappings:
        require(isinstance(item, dict), "legacy mapping entry must be an object")
        legacy_name = item["legacyResponsibility"]
        roles = item["universalRoles"]
        require(isinstance(legacy_name, str), "legacy responsibility must be a string")
        require(legacy_name not in observed_legacy, f"duplicate legacy mapping: {legacy_name}")
        observed_legacy.add(legacy_name)
        require(isinstance(item["owner"], str) and item["owner"], f"legacy mapping has no owner: {legacy_name}")
        require(isinstance(roles, list), f"legacy mapping roles must be a list: {legacy_name}")
        for role in roles:
            require(role in catalog_names, f"legacy mapping references unknown role: {role}")
    require(expected_legacy <= observed_legacy, "legacy mappings are incomplete")

    mappings = mapping["mappings"]
    require(isinstance(mappings, list), "mappings must be a list")
    expected_responsibilities = {
        "scope_and_triage",
        "recon_and_architecture_mapping",
        "bounded_audit_and_evidence_collection",
        "specialist_investigation",
        "plan_authoring_and_migration_design",
        "evidence_judgment_and_plan_critique",
        "approved_plan_execution",
        "mechanical_follow_up",
        "final_acceptance_and_recovery",
    }
    observed_responsibilities: set[str] = set()
    mapped_roles: set[str] = set()
    for item in mappings:
        require(isinstance(item, dict), "mapping entry must be an object")
        responsibility = item["responsibility"]
        roles = item["universalRoles"]
        require(isinstance(responsibility, str), "mapping responsibility must be a string")
        require(responsibility not in observed_responsibilities, f"duplicate responsibility: {responsibility}")
        observed_responsibilities.add(responsibility)
        require(isinstance(roles, list) and roles, f"mapping has no roles: {responsibility}")
        require(isinstance(item["selection"], str) and item["selection"], f"mapping has no selection: {responsibility}")
        for role in roles:
            require(role in catalog_names, f"mapping references unknown universal role: {role}")
            mapped_roles.add(role)

    require(expected_responsibilities <= observed_responsibilities, "mapping responsibilities are incomplete")
    require(
        {"repository_mapper", "feature_implementer", "large_implementer", "acceptance_integrator"} <= mapped_roles,
        "essential universal roles are not mapped",
    )
    require(not (SKILL / "assets" / "worker-matrix.json").exists(), "legacy worker matrix remains")
    legacy_workers = SKILL / "assets" / "workers"
    require(not any(legacy_workers.glob("*.md")), "legacy project worker prompts remain")


def validate_links() -> None:
    required = ["workers.md", "audit.md", "plans.md", "runtime-ci.md", "execute-reconcile.md"]
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    worker_text = (SKILL / "references" / "workers.md").read_text(encoding="utf-8")
    require("TODO" not in skill_text, "SKILL.md contains TODO placeholders")
    require("universal-role-mappings.json" in worker_text, "worker docs do not route to the mapping")
    require("global doctor" in worker_text, "worker docs do not require the global doctor")
    require("project-local worker files" in skill_text, "setup compatibility is not documented")
    for filename in required:
        require((SKILL / "references" / filename).is_file(), f"missing reference: {filename}")
        require(filename in skill_text, f"SKILL.md does not route to {filename}")

    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            SKILL / "SKILL.md",
            SKILL / "references" / "audit.md",
            SKILL / "references" / "plans.md",
            SKILL / "references" / "runtime-ci.md",
            SKILL / "references" / "execute-reconcile.md",
            SKILL / "references" / "workers.md",
        ]
    )
    for legacy_requirement in [
        "Execute only an approved plan, only with Luna",
        "Have Luna",
        "Pass Luna",
        "Luna receives",
        "Generated agent names",
        "creates one file for each unique role",
    ]:
        require(legacy_requirement not in source_text, f"legacy routing remains: {legacy_requirement}")


def validate_setup() -> None:
    setup = SKILL / "scripts" / "setup_agents.py"

    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        project = base / "project"
        codex_home = base / "codex"
        routing_root = codex_home / "skills" / "subagent-routing"
        doctor = routing_root / "scripts" / "sync-universal-roles.py"
        project.mkdir()
        doctor.parent.mkdir(parents=True)
        doctor.write_text(
            "\n".join(
                [
                    "import json",
                    "import sys",
                    "if sys.argv[1:3] != ['--check', '--json']:",
                    "    raise SystemExit(9)",
                    "if sys.argv[3] != '--codex-home':",
                    "    raise SystemExit(8)",
                    "print(json.dumps({'status': 'ok', 'checks': [{'code': 'fixture', 'status': 'pass'}]}))",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        command = [
            sys.executable,
            str(setup),
            "--project",
            str(project),
            "--codex-home",
            str(codex_home),
            "--yes",
            "--dry-run",
            "--catalog",
            str(base / "legacy-model-catalog.json"),
            "--json",
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        require(result.returncode == 0, f"compatibility setup failed: {result.stderr}")
        payload = json.loads(result.stdout)
        compatibility = payload["compatibility"]
        require(payload["status"] == "ok", "compatibility setup did not report success")
        require(compatibility["createdProjectWorkers"] is False, "setup reported project worker creation")
        require("--project" in compatibility["ignoredLegacyOptions"], "project compatibility missing")
        require("--yes" in compatibility["ignoredLegacyOptions"], "yes compatibility missing")
        require("--dry-run" in compatibility["ignoredLegacyOptions"], "dry-run compatibility missing")
        require("--catalog" in compatibility["ignoredLegacyOptions"], "catalog compatibility missing")
        require(payload["doctorReport"]["status"] == "ok", "global doctor result was not retained")
        require(not (project / ".codex" / "agents").exists(), "setup created project agents")

        unavailable = subprocess.run(
            [
                sys.executable,
                str(setup),
                "--project",
                str(project),
                "--codex-home",
                str(codex_home),
                "--routing-root",
                str(base / "missing-routing"),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        require(unavailable.returncode == 2, "missing global doctor must block setup")
        blocked = json.loads(unavailable.stdout)
        require(blocked["status"] == "blocked", "missing global doctor must report BLOCKED")
        require(blocked["compatibility"]["createdProjectWorkers"] is False, "blocked setup created workers")


def validate_eval_cases() -> None:
    cases = load_json(PLUGIN / "eval" / "cases.json")
    require(len(cases["expected_findings"]) >= 2, "not enough expected findings")
    require(len(cases["expected_rejections"]) >= 2, "not enough expected rejections")
    for relative in cases["fixture_files"]:
        require((PLUGIN / "eval" / "fixtures" / "demo-repo" / relative).is_file(), f"missing fixture file: {relative}")

    routing = cases["routing_expectations"]
    require(isinstance(routing, dict), "routing expectations must be an object")
    require(routing["setup"]["creates_project_workers"] is False, "eval allows project workers")
    require(routing["luna_gate"]["when_unproven"] == "BLOCKED", "eval does not preserve Luna gate")
    expected_roles = {"repository_mapper", "feature_implementer", "acceptance_integrator"}
    observed_roles = {item["role"] for item in routing["universal_roles"]}
    require(expected_roles <= observed_roles, "eval is missing universal-role expectations")


def main() -> int:
    validate_manifest()
    validate_universal_mapping()
    validate_links()
    validate_setup()
    validate_eval_cases()
    print("Codex Improve universal role validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
