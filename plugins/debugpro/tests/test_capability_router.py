import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_debugpro  # noqa: E402


class CapabilityRouterTests(unittest.TestCase):
    def router_text(self) -> str:
        path = PLUGIN_ROOT / validate_debugpro.ROUTER_REFERENCE
        if not path.exists():
            self.fail(f"missing required router reference: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    def agent_text(self) -> str:
        path = PLUGIN_ROOT / validate_debugpro.ROUTER_AGENT
        if not path.exists():
            self.fail(f"missing required router agent: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    def integrations_text(self) -> str:
        path = PLUGIN_ROOT / "skills/debugpro/references/capability-integrations.md"
        if not path.exists():
            self.fail(f"missing required integrations reference: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    def intake_text(self) -> str:
        path = PLUGIN_ROOT / "skills/debugpro-intake/SKILL.md"
        if not path.exists():
            self.fail(f"missing required intake skill: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    def output_contracts_text(self) -> str:
        path = PLUGIN_ROOT / "skills/debugpro/references/output-contracts.md"
        if not path.exists():
            self.fail(f"missing required output contracts reference: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    def test_router_has_required_capability_sections(self) -> None:
        missing = validate_debugpro.missing_router_sections(self.router_text())
        self.assertEqual(missing, [])

    def test_router_covers_required_use_cases(self) -> None:
        missing = validate_debugpro.missing_use_cases(self.router_text())
        self.assertEqual(missing, [])

    def test_router_agent_uses_compact_packet_format(self) -> None:
        missing = validate_debugpro.missing_agent_fields(self.agent_text())
        self.assertEqual(missing, [])

    def test_tool_finder_rules_are_scoped_to_maintenance(self) -> None:
        combined = "\n".join([self.router_text(), self.agent_text(), self.integrations_text()])
        self.assertIn("Tool Finder is a maintenance and discovery aid", combined)
        self.assertIn("not a default debugging probe", combined)
        self.assertIn("do not list Tool Finder unless discovery", combined)
        self.assertIn("label Tool Finder as `[optional]`", combined)

    def test_popup_intake_is_gated_and_recorded(self) -> None:
        combined = "\n".join(
            [
                self.router_text(),
                self.agent_text(),
                self.intake_text(),
                self.output_contracts_text(),
            ]
        )
        self.assertIn("request_user_input", combined)
        self.assertIn("first route is ambiguous or evidence is missing", combined)
        self.assertIn("Do not prompt when existing source, log, test, or runtime evidence already proves the route", combined)
        self.assertIn("at least three user-owned answers", combined)
        self.assertIn("symptom/impact", combined)
        self.assertIn("reproduction or evidence source", combined)
        self.assertIn("safety boundary or desired next action", combined)
        self.assertIn("explicit exception", combined)
        self.assertIn("User input rounds", combined)


if __name__ == "__main__":
    unittest.main()
