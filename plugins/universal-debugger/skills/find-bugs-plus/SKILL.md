---
name: find-bugs-plus
description: Use when finding or fixing bugs from diffs, tests, logs, stack traces, Sentry events, or same-surface adjacent defects during approved fixes.
---

# Find Bugs Plus

Find real defects by proving the failure path before reporting or fixing. Use it for branch review, live symptoms, and bounded adjacent-defect sweeps while an approved fix is in progress.

## When To Use

Use this for bug hunts, failure triage, and fix-time related-defect searches. Use `debugging-strategies` for technique-only questions and `master-debugger` when root-cause ownership is needed.

## Mode Selection

Use `references/evidence-modes.md` for diff review and failure investigation. Use `references/adjacent-defect-sweep.md` when the user asked for a fix and the touched surface is known. If the symptom is unresolved or broad, route through `universal-debugger` or `master-debugger` first.

## Workflow

1. Capture the boundary: bug-hunt only, fix requested, or fix plus adjacent sweep.
2. Collect evidence with the smallest useful command set.
3. Reproduce the symptom or identify the closest observable signal.
4. Classify the issue source: input/contract, state/data, async/race, dependency/env, auth/security, performance/resource, or regression.
5. Rank falsifiable hypotheses and test one at a time.
6. Report only defects backed by evidence. If fixing is requested, make the smallest verified fix.
7. During a fix, search the same touched surface for adjacent defects and fix only same-root-cause, same-contract, or same-validation-path defects.
8. Verify the original symptom and each adjacent fix with targeted tests, commands, or explicit blockers.

```bash
python scripts/collect_bug_context.py --repo <path>
```

If evidence starts with a diff, use diff review. If it starts with a failing command, stack trace, log, or Sentry event, use failure investigation. If code changes, run the adjacent sweep before final verification.

## Guardrails

- Do not invent findings, run unbounded whole-repo hunts, stack unrelated fixes, edit during review-only requests, or claim a fix without verification.
- Pitfall: pattern matches are leads, not findings, until a runtime path is traced.

## References

- `references/evidence-modes.md` - diff, test, log, stack trace, Sentry, and production-symptom investigation modes.
- `references/adjacent-defect-sweep.md` - when to search for related bugs during implementation and when to stop.
- `references/output-contract.md` - required finding, fix, and handoff formats.
