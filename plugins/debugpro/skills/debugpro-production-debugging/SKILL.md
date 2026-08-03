---
name: debugpro-production-debugging
description: Use when production logs, traces, metrics, deploys, or flags are the main evidence.
---

# DebugPro Production Debugging

Use when observability is stronger than local reproduction.

## Evidence Sources

Prefer ids, metric windows, deploys, log queries, cohorts, and flag state.
Use `../debugpro/references/capability-router.md` to choose optional observability, deploy, database, or cloud connectors and their fallbacks.

## Workflow

1. Capture symptom and impact without assuming local reproduction exists.
2. Anchor claims to ids, metric windows, deploys, or log queries.
3. Compare before/after deploy, migration, config, and flag windows.
4. Generate falsifiable hypotheses using `debugpro-hypotheses`.
5. Prefer read-only probes; mutate only with explicit bounded approval.
6. Separate containment from root-cause fixes.
7. Verify with the original signal.

## Output

```markdown
## Production Debug Report
- Symptom/impact:
- Evidence checked:
- Timeline:
- Hypotheses:
- Cause:
- Containment:
- Fix:
- Verification:
- Residual risk:
```

Treat observability as evidence. If a source is unavailable, state that and use the closest signal.
