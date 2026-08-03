---
name: debugpro-arbitration
description: Use when investigated debugging hypotheses must be compared before choosing a fix.
---

# DebugPro Arbitration

Use after competing hypotheses have been investigated. Use
`../debugpro/references/parallel-debugging-contract.md` for the shared
arbitration contract when reports came from parallel tracks.

## Inputs

Collect symptom, verdicts, evidence, contradictions, confidence, and residual risk.
Include the routing packet from `debugpro-capability-router` when one was used.

## Arbitration Steps

1. Reject hypotheses contradicted by direct evidence.
2. Rank plausible causes by evidence strength, causal chain, reproducibility, and contradictions.
3. Identify compound causes when confirmed hypotheses are linked.
4. If no hypothesis is confirmed, produce the next smallest probe plan instead of guessing.
5. Produce one final handoff.

## Output

Use `../debugpro/references/handoff-report-template.md`. Include the full hypothesis table:

```markdown
| Hypothesis | Verdict | Confidence | Key Evidence | Next Action |
| --- | --- | --- | --- | --- |
```

Do not recommend a code change unless evidence supports it or clearly label it a bounded experiment.
