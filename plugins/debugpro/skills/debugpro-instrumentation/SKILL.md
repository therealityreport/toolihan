---
name: debugpro-instrumentation
description: Use when existing evidence is insufficient and bounded probes are needed to prove cause.
---

# DebugPro Instrumentation

Use this technique to add temporary or durable observability that answers a specific debugging question.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`, `../debugpro/references/missing-evidence-routing.md`.

## When To Use

- Logs, traces, metrics, screenshots, or test output do not expose the deciding state.
- A hypothesis needs one focused probe before a fix is safe.
- The system needs durable diagnostics around a high-risk boundary.

## Required Setup And Evidence

- The exact question the instrumentation must answer.
- Current evidence and the gap it leaves.
- Safe location for a probe: log, assertion, metric, trace span, event, screenshot, dump, or test helper.
- Privacy, secret, performance, and noise constraints.
- Removal plan for temporary probes or ownership plan for durable diagnostics.

## Procedure

1. State the hypothesis or unknown that the probe will decide.
2. Choose the least invasive probe that captures the needed state.
3. Include correlation identifiers, timestamps, inputs, outputs, and boundary names when useful.
4. Avoid secrets, tokens, private data, or high-cardinality noise.
5. Run the repro and capture the probe output.
6. Remove temporary probes after use, or keep durable probes only when they are intentionally scoped and useful.

## Route-Specific Fallbacks And Stop Conditions

- If adding a probe would change timing or behavior materially, use read-only logs, traces, profiler output, or debugger inspection first.
- If probe placement is unclear, route to `debugpro-root-cause-tracing`.
- Stop if instrumentation would expose secrets, alter production behavior unsafely, or create broad logging noise.
- If the probe disproves the current hypothesis, return to `debugpro-hypotheses`.

## Output Format

```markdown
## Instrumentation Result
- Question:
- Probe added:
- Evidence captured:
- Answer:
- Temporary cleanup:
- Durable diagnostics kept:
- Risks avoided:
- Next route:
```
