---
name: debugpro-bug-hunt
description: Use when diffs, logs, traces, or stacks need evidence-backed bug finding.
---

# DebugPro Bug Hunt

Use this route for review-only bug finding, diff audits, stack trace triage, Sentry/log event triage, and static bug hunts where findings must be proven before reporting.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/evidence-modes.md`
- `../debugpro/references/output-contracts.md`
- `../debugpro/references/bug-patterns.md`

## When To Use

- The user asks to find bugs, review for bugs, inspect a diff, or triage a stack trace/log/event.
- The task is not yet an approved implementation fix.
- A same-surface adjacent check is needed before or after a focused fix handoff.

## Workflow

1. Capture the boundary: review-only, triage-only, fix requested, or adjacent sweep.
2. Select the narrowest evidence mode from `evidence-modes.md`.
3. Read changed files plus only callers, tests, schemas, migrations, config, or runtime artifacts needed to prove a failure path.
4. Classify each lead: input/contract, state/data, async/race, dependency/env, auth/security, performance/resource, regression, or runtime drift.
5. Report only defects backed by direct evidence. Pattern matches are leads until a failure path is traced.
6. If a fix is approved, route through `debugpro-root-cause-tracing`, `debugpro-verify`, and `debugpro-adjacent-sweep` rather than broadening this route.

## Guardrails

- Do not invent findings or report speculative risks as confirmed bugs.
- Do not run an unbounded whole-repo hunt.
- Do not edit code during review-only requests.
- Do not treat missing search results as proof unless runtime or contract evidence supports the conclusion.

## Output

Use the finding format in `../debugpro/references/output-contracts.md`. If no confirmed findings exist, say what was reviewed and why no reportable defect was found.
