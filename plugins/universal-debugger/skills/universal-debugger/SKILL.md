---
name: universal-debugger
description: Use when debugging failed tests, exceptions, regressions, incidents, logs/traces, or unclear symptoms; skip generic feature work.
---

# Universal Debugger

Routing and operating layer for debugging work. Any codebase can start here, but diagnosis still needs access, evidence, reproduction or equivalent signal, logs/tests/traces, environment details, and task context.

## First-Screen Routing

| Situation | Route |
| --- | --- |
| Active unresolved failure, regression, failed test, exception, incident, or unknown root cause | `master-debugger` |
| Bug hunt, branch review, stack trace/log/Sentry triage, or adjacent-defect sweep during an approved fix | `find-bugs-plus` |
| Debugger/profiler/log/crash technique or checklist question | `debugging-strategies` |
| Multiple credible causes or user-approved independent tracks | `parallel-debugging` |
| Explicit Superpowers or strict four-phase request | `superpowers:systematic-debugging` |

If the issue is ambiguous, stay here long enough to collect intake and choose a route. Do not duplicate the full contents of the downstream debugging skills.

## Required Intake

Collect or state what is missing:

Symptom/impact, reproduction or closest signal, expected versus actual behavior, environment, recent changes, scope, and available logs/tests/traces/screenshots/metrics/error text.

## Operating Rules

1. Prove or bound the root cause before proposing fixes.
2. Build the smallest useful reproduction or evidence loop first.
3. Form falsifiable hypotheses when the cause is not obvious.
4. Probe one hypothesis at a time and map each probe to the evidence it should produce.
5. Apply one minimal fix only after the cause is supported by evidence.
6. While fixing, run a bounded adjacent-defect sweep on the same touched surface and same root-cause family.
7. Verify against the original symptom, then add prevention when the codebase has a real seam for it.

Forbidden: guessing, stacking unrelated fixes, broad log spam, unrequested subagents, or claiming diagnosis without access/evidence/repro/logs/tests/context.

## References

- `references/routing-matrix.md` - prompt shapes, routing conflicts, and when to stay in this skill.
- `references/debugging-operating-model.md` - intake, root-cause loop, stop rules, and cross-codebase limits.
- `references/parallel-investigation-template.md` - safe split for independent hypotheses after explicit permission.
- `references/handoff-report-template.md` - evidence-backed handoff format and validation checklist.
- `../find-bugs-plus/SKILL.md` - bug-hunting, diff review, Sentry/log/test triage, and adjacent-defect sweep workflow.

## Handoff Shape

Use this evidence-backed format for summaries and handoffs:

1. `Root Cause`
2. `Evidence`
3. `Minimal Reproduction or Failing Test`
4. `Fix`
5. `Prevention`
6. `Open Questions`
