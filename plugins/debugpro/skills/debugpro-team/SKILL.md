---
name: debugpro-team
description: Use when multiple independent debugging hypotheses can be investigated safely in parallel before arbitration and fixes.
---

# DebugPro Team

Coordinate safe parallel debugging only when
`../debugpro/references/parallel-debugging-contract.md` passes. Use this after
intake and hypothesis generation, not as a first step for unclear failures.

## Entry Requirements

All requirements must be true:

- The symptom and current evidence are written down.
- `parallel-debugging-contract.md` passes its gate.
- The team has one coordinator who owns arbitration before fixes.

If the contract fails, run the highest-value single probe first.

## Coordination Flow

1. Restate the symptom, constraints, and stop conditions in simple terms.
2. Build a track table with one hypothesis per row.
3. Assign each track to `debugpro-investigator` when available, or run the same investigator protocol serially.
4. Use the track packet and investigator report from `parallel-debugging-contract.md`.
5. Collect investigator reports without merging conclusions early.
6. Route results to `debugpro-arbitration`.

## Output

For planning-only requests, return the lightweight packet:

```markdown
## Parallel Investigation Plan
- Symptom:
- Safety gate result:
- Tracks:
- Serialized fallback:
- Arbitration owner:
```

After investigation starts, return the full coordination packet:

```markdown
## DebugPro Team Packet

### Symptom

### Safety Gate

### Track Assignments
| Track | Hypothesis | Scope | Investigator | Status |
| --- | --- | --- | --- | --- |

### Investigator Results
| Track | Verdict | Confidence | Key Evidence | Contradictions | Next Probe |
| --- | --- | --- | --- | --- | --- |

### Arbitration Required Before Fix
- Route: debugpro-arbitration
- Reason:
```
