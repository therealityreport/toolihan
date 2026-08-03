"""DebugPro validation constants."""

from __future__ import annotations

from pathlib import Path


ROUTER_REFERENCE = Path("skills/debugpro/references/capability-router.md")
ROUTER_AGENT = Path("agents/debugpro-capability-router.md")
ROOT_SKILL = Path("skills/debugpro/SKILL.md")
README = Path("README.md")
MANIFESTS = (Path(".codex-plugin/plugin.json"),)

REQUIRED_ROUTER_SECTIONS = (
    "Skills",
    "Agents",
    "References",
    "Tools And CLIs",
    "MCPs And Connectors",
    "Fallbacks",
    "Stop Conditions",
)

REQUIRED_AGENT_FIELDS = (
    "Primary route:",
    "Why:",
    "Required evidence:",
    "References to open:",
    "Tools/CLIs/MCPs/connectors to use:",
    "Capability availability:",
    "Fallbacks if unavailable:",
    "Parallel escalation:",
    "Stop conditions:",
)

REQUIRED_USE_CASES: dict[str, tuple[tuple[str, ...], ...]] = {
    "Missing symptom/evidence": (("missing symptom", "evidence"), ("missing evidence", "symptom")),
    "Unclear root cause": (("unclear root cause",),),
    "Independent hypotheses": (("independent hypotheses",), ("parallel hypotheses", "independent probes")),
    "Bug hunt": (("bug hunt",), ("diff audit",), ("event triage",)),
    "Browser/localhost/UI runtime failure": (
        ("browser localhost ui runtime failure",),
        ("browser", "localhost", "ui runtime"),
    ),
    "CI/PR failure": (("ci pr failure",), ("ci", "pr", "failure")),
    "MCP/runtime ownership failure": (("mcp runtime ownership failure",), ("mcp runtime ownership",)),
    "Source/runtime/cache drift": (("source runtime cache drift",), ("source runtime", "cache drift")),
    "Production/staging incident": (("production staging incident",), ("production", "staging", "incident")),
    "Flaky tests": (("flaky tests",),),
    "Regression window": (("regression window",),),
    "Minimal repro needed": (("minimal repro needed",), ("minimal repro",), ("minimal reproduction",)),
    "Performance issue": (("performance issue",),),
    "macOS app issue": (("macos app issue",), ("macos", "app issue")),
    "External library/API/CLI uncertainty": (
        ("external library api cli uncertainty",),
        ("external library", "api", "cli", "uncertainty"),
    ),
    "Fix approved and same surface may hide nearby bugs": (
        ("fix approved", "same surface"),
        ("approved fix", "same surface"),
        ("same surface", "nearby bugs"),
    ),
}
