import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_debugpro  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_manifest(path: Path, *, unsupported: bool = False) -> None:
    manifest = {
        "name": "debugpro",
        "version": "0.3.0",
        "description": "Evidence-first debugging.",
        "author": {"name": "DebugPro"},
        "homepage": "https://example.test/debugpro",
        "repository": "https://example.test/debugpro.git",
        "license": "MIT",
        "keywords": ["debugging"],
        "skills": "./skills/",
        "interface": {
            "displayName": "DebugPro",
            "shortDescription": "Evidence-first debugging.",
            "longDescription": "Evidence-first debugging for Codex.",
            "developerName": "DebugPro",
            "category": "Coding",
            "capabilities": ["Read"],
            "websiteURL": "https://example.test/debugpro",
            "defaultPrompt": ["Debug this failure."],
        },
    }
    if unsupported:
        manifest["interface"]["includes"] = []
    write(
        path,
        json.dumps(manifest, indent=2, sort_keys=True),
    )


def write_valid_fixture(root: Path) -> None:
    router = """
# Capability Router

## Purpose

Select the first useful DebugPro route.

## How To Use This Router

Read the symptom, evidence, environment, and tool availability.

## Use-Case Matrix

| Use Case | First Owner | Optional Capabilities |
| --- | --- | --- |
| Missing symptom/evidence | `debugpro-intake` | shell inventory, logs |
| Unclear root cause | `debugpro-hypotheses` | `debugpro-capability-router` |
| Independent hypotheses | `debugpro-team` | Agent Teams |
| Bug hunt | `debugpro-bug-hunt` | diff audit, event triage |
| Browser/localhost/UI runtime failure | `debugpro-browser-runtime-proof` | Browser, Chrome |
| CI/PR failure | `debugpro-ci-pr-failure` | GitHub MCP, `gh` |
| MCP/runtime ownership failure | `debugpro-mcp-runtime-ownership` | MCP Inspector |
| Source/runtime/cache drift | `debugpro-source-runtime-parity` | `diff`, `rg` |
| Production/staging incident | `debugpro-production-debugging` | Render, Sentry |
| Flaky tests | `debugpro-flaky` | repeat loops |
| Regression window | `debugpro-bisect` | `git bisect` |
| Minimal repro needed | `debugpro-delta` | fixture minimization |
| Performance issue | `debugpro-performance` | traces |
| macOS app issue | `debugpro-macos-debugging` | `xcodebuild` |
| External library/API/CLI uncertainty | selected domain skill plus docs lookup | Context7 |
| Fix approved and same surface may hide nearby bugs | `debugpro-adjacent-sweep` | focused review |

## Skills

Use DebugPro skills as primary route owners.

## Agents

Use DebugPro agents only when routing or investigation delegation is justified.

## References

Open the route-specific references named by the selected owner.

## Tools And CLIs

Use local tools and CLIs only when they answer the evidence question.

## MCPs And Connectors

Use MCPs and connectors when they provide the needed live surface.

## Fallbacks

When a capability is unavailable, choose the smallest local fallback.

## Stop Conditions

Stop when the next step is destructive, ambiguous, or credential-bound.

## Smoke Prompts

Use representative browser, CI, MCP, source/runtime, production, flaky,
performance, macOS, unclear-cause, and adjacent-sweep prompts.
"""
    agent = """
# DebugPro Capability Router

Primary route:
Why:
Required evidence:
References to open:
Tools/CLIs/MCPs/connectors to use:
Capability availability:
Fallbacks if unavailable:
Parallel escalation:
Stop conditions:
"""
    readme = """
# DebugPro

The capability router chooses the broad tool and evidence bundle.
Capability routing decides which capabilities to use first, skill routing picks
the specific DebugPro skill, and technique indexing explains debugging methods.
"""
    write(root / validate_debugpro.ROUTER_REFERENCE, router)
    write(root / validate_debugpro.ROUTER_AGENT, agent)
    write(root / validate_debugpro.ROOT_SKILL, "Use references/capability-router.md first.\n")
    write(root / validate_debugpro.README, readme)
    for manifest in validate_debugpro.MANIFESTS:
        write_manifest(root / manifest)


class DebugProValidationTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_fixture(root)
            self.assertEqual(validate_debugpro.validate(root), [])

    def test_missing_router_surface_fails_with_specific_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / validate_debugpro.ROOT_SKILL, "No router here.\n")
            write(root / validate_debugpro.README, "# DebugPro\n")
            for manifest in validate_debugpro.MANIFESTS:
                write_manifest(root / manifest, unsupported=True)

            codes = {item.code for item in validate_debugpro.validate(root)}

        self.assertIn("missing_capability_router_reference", codes)
        self.assertIn("missing_capability_router_agent", codes)
        self.assertIn("root_skill_router_missing", codes)
        self.assertIn("manifest_schema_invalid", codes)
        self.assertIn("readme_router_explanation_missing", codes)

    def test_live_plugin_satisfies_v4_validation_contract(self) -> None:
        diagnostics = validate_debugpro.validate(PLUGIN_ROOT)
        details = "\n".join(f"{item.code}: {item.path}: {item.message}" for item in diagnostics)
        self.assertEqual(diagnostics, [], details)

    def test_release_validation_includes_current_codex_schema(self) -> None:
        diagnostics = validate_debugpro.validate(PLUGIN_ROOT)
        details = "\n".join(f"{item.code}: {item.path}: {item.message}" for item in diagnostics)
        self.assertEqual(diagnostics, [], details)

    def test_manifest_contract_rejects_unknown_fields_and_bad_semver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_fixture(root)
            manifest_path = root / validate_debugpro.MANIFESTS[0]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "dev"
            manifest["mystery"] = True
            write(manifest_path, json.dumps(manifest))

            diagnostics = validate_debugpro.validate(root)

        self.assertIn("manifest_schema_invalid", {item.code for item in diagnostics})


if __name__ == "__main__":
    unittest.main()
