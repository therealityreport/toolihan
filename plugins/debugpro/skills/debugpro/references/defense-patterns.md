# Defense Patterns

Use after root cause is supported and the fix surface is known.

| Risk | Defense |
| --- | --- |
| Regression in pure logic | Focused unit test or property check. |
| Integration contract drift | Contract test, schema validation, or fixture. |
| Runtime/cache drift | Version stamp, parity check, publish validation, or install proof. |
| Config/env drift | Config validation, startup warning, or typed settings. |
| Browser/UI regression | Component test, route smoke, screenshot check, or console check. |
| CI workflow breakage | Workflow lint, reusable job, pinned action, or documented runner version. |
| MCP ownership confusion | Health command, discovery check, and config ownership doc. |
| Production incident | Alert, dashboard, runbook, or deploy gate tied to the failure mode. |
| Flaky behavior | Isolation fixture, deterministic seed, cleanup hook, or polluter check. |

## Rule

Add defenses that match the project's existing patterns. Do not invent a broad
test harness or monitoring stack just to close a narrow bug.
