---
name: debugpro-hypotheses
description: Use when intake is complete but the cause remains unclear.
---

# DebugPro Hypotheses

Generate 3-5 competing hypotheses before changing code. Each must be specific enough to be wrong.
Use `../debugpro/references/missing-evidence-routing.md` when the next missing
signal could require intake, tracing, instrumentation, or a domain route.

## Failure Categories

Cover different categories when plausible: logic, data shape, state, integration, resources, or runtime drift.

## Required Hypothesis Shape

For each hypothesis include:

```markdown
### H1: Short Title
- Category:
- Statement:
- Confirming evidence:
- Falsifying evidence:
- Probe plan:
- Expected output:
- Confidence: High | Medium | Low
- Scope:
```

## Rules

- Use current evidence; do not invent facts.
- Prefer probes that read code, tests, logs, traces, config, database state, or UI/runtime state.
- Do not propose fixes until a hypothesis is confirmed or strongly supported.
- If all hypotheses share the same probe, stay single-threaded.
- If the right route or tool bundle is unclear, use `debugpro-capability-router`.
- If two or more hypotheses have independent read-only probes, consider `debugpro-team` as an escalation.
