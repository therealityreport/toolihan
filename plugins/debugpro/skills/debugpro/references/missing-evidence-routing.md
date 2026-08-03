# DebugPro Missing-Evidence Routing

Use this table when a request has a symptom but the next diagnostic move is
unclear because evidence is missing.

## Routing Table

| Missing evidence | Primary route | Rule |
| --- | --- | --- |
| Basic symptom, impact, expected behavior, actual behavior, environment, or exact error | `debugpro-intake` | Ask for the smallest facts needed to route. |
| Repro exists but the responsible layer is unclear | `debugpro-hypotheses` | Build falsifiable causes before probing. |
| A value, state, response, render, or side effect is wrong but the first wrong boundary is unknown | `debugpro-root-cause-tracing` | Walk upstream boundary by boundary. |
| The deciding state is invisible in current logs, tests, UI, traces, or metrics | `debugpro-instrumentation` | Add or select one bounded probe that answers a specific question. |
| Source, cache, install, package, generated output, or live runtime may disagree | `debugpro-source-runtime-parity` | Prove the executing copy before editing. |
| Browser, localhost, UI, console, network, or DOM state is the missing proof | `debugpro-browser-runtime-proof` | Capture direct runtime evidence. |
| CI job, workflow step, PR check, runner context, or annotation is missing | `debugpro-ci-pr-failure` | Start from the first failing CI signal. |
| MCP, plugin, connector, or tool ownership is missing or stale | `debugpro-mcp-runtime-ownership` | Map configured, installed, exposed, and callable ownership. |
| The same signal sometimes passes and sometimes fails | `debugpro-flaky` | Capture pass/fail rate, seed, order, timing, and polluter evidence. |
| The failure is broad and needs a smaller trigger | `debugpro-delta` | Reduce while preserving the original failure signature. |

## Decision Rules

- If more than one row applies, choose the route that can produce the first
  direct evidence with the least mutation.
- Use native `request_user_input` popup intake only when the first route is
  ambiguous or evidence is missing after source, log, test, runtime, and
  user-provided evidence are checked.
- Do not prompt when existing source, log, test, or runtime evidence already
  proves the route.
- The first compact popup must ask for symptom/impact, reproduction or evidence
  source, and safety boundary or desired next action.
- Require at least three user-owned answers for the popup intake path unless an
  explicit exception is recorded.
- If the needed evidence source is unavailable, state that boundary and use the
  nearest evidence-backed substitute.
- If all candidate routes need the same first probe, stay single-threaded.
- If independent read-only probes remain after hypotheses are formed, use
  `parallel-debugging-contract.md` before escalation.

## Output Fields

When missing evidence blocks diagnosis, report:

```markdown
## Missing Evidence Routing
- Symptom:
- Missing evidence:
- Chosen route:
- Why this route:
- Nearest available substitute:
- Stop condition or next probe:

## User input rounds
- Round 1:
  - Symptom/impact:
  - Reproduction or evidence source:
  - Safety boundary or desired next action:
  - Exception recorded:
```
