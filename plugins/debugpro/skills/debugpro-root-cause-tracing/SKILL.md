---
name: debugpro-root-cause-tracing
description: Use when a symptom needs a proven chain from trigger to defective state.
---

# DebugPro Root Cause Tracing

Use this technique to trace a failure backward through data, control flow, state transitions, and runtime boundaries until the first wrong condition is proven.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`, `../debugpro/references/missing-evidence-routing.md`.

## When To Use

- The failure is reproducible but the responsible layer is unclear.
- The bug crosses code, data, config, cache, runtime, service, UI, or deployment boundaries.
- A fix would be speculative without a cause chain.

## Required Setup And Evidence

- Exact symptom, expected result, and actual result.
- Repro command or workflow.
- Current source, config, runtime, logs, traces, database rows, request/response examples, or UI state relevant to the symptom.
- Known boundary points where the value/state should be correct.
- Any recent changes or suspected drift.

## Procedure

1. Write the observed failure as a concrete wrong value, state, call, response, render, or side effect.
2. Identify the downstream point where the wrong state is visible.
3. Walk upstream one boundary at a time: caller, transform, persistence, cache, transport, config, runtime, and input.
4. At each boundary, record the expected value, observed value, and evidence source.
5. Stop when the first wrong boundary is proven and the upstream input is still correct.
6. Propose the smallest fix that corrects that boundary and preserves the expected contract.

## Route-Specific Fallbacks And Stop Conditions

- If evidence is missing at a key boundary, route to `debugpro-instrumentation`.
- If multiple plausible causes remain, route to `debugpro-hypotheses`.
- If source and runtime disagree, route to `debugpro-source-runtime-parity` when available.
- Stop before changing code if the first wrong boundary is not proven.

## Output Format

```markdown
## Root Cause Trace
- Symptom:
- Repro:
- Boundary map:
- First wrong boundary:
- Evidence:
- Upstream correct proof:
- Root cause:
- Smallest fix:
- Stop conditions hit:
```
