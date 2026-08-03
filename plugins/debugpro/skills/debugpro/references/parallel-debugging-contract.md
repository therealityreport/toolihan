# DebugPro Parallel Debugging Contract

Use this contract before running multi-track debugging, subagents, or parallel
tool probes. Parallel debugging is an escalation path, not the default response
to uncertainty.

## When Parallel Work Is Allowed

All answers must be `Yes` before parallel work starts:

```markdown
Independent hypotheses: Yes | No
Read-only or disjoint probes: Yes | No
Disjoint files, services, data, or runtime state: Yes | No
Clear confirm/falsify criteria per track: Yes | No
One arbitration owner before fixes: Yes | No
```

If any answer is `No`, run the highest-value single probe first.

## Track Contract

Each track gets exactly one hypothesis and one evidence scope.

```markdown
## Track H#
- Symptom:
- Hypothesis:
- Scope:
- Allowed evidence sources:
- Confirming evidence criteria:
- Falsifying evidence criteria:
- Stop conditions:
- Report required: verdict, confidence, evidence for, evidence against, causal chain, contradictions, next probe.
```

Tracks must not share mutable state, edit the same files, run destructive probes,
or merge conclusions before arbitration.

## Investigator Report

```markdown
## Investigation Report: H#
- Verdict: Confirmed | Falsified | Inconclusive
- Confidence: High | Medium | Low
- Evidence for:
- Evidence against:
- Causal chain:
- Contradictions:
- Residual risk:
- Next probe:
```

## Arbitration Contract

No fix is allowed until arbitration compares:

- each verdict;
- confidence;
- evidence for and against;
- causal chain strength;
- contradictions;
- residual risk;
- next probe recommendations.

If no hypothesis is confirmed, produce the next smallest probe plan instead of a
fix.

## Output Contract

Parallel coordination should end with a compact table and a clear arbitration
status:

```markdown
| Track | Verdict | Confidence | Key Evidence | Contradictions | Next Probe |
| --- | --- | --- | --- | --- | --- |
```

State whether the result is ready for a fix, needs another probe, or is blocked
by missing evidence.
