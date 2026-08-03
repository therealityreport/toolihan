---
name: debugpro-delta
description: Use when a failure needs a minimal reproducible input, fixture, config, or project.
---

# DebugPro Delta

Use this technique to reduce a failure to the smallest case that still proves the bug.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`.

## When To Use

- The failure depends on a large input, fixture, config, dataset, route, dependency graph, or project shape.
- The current repro is too broad to identify the faulty condition.
- A minimal repro would make the fix safer or make an upstream/library report credible.

## Required Setup And Evidence

- Original failing command or workflow.
- Expected behavior and actual failure evidence.
- The full input/config/project that reproduces the failure.
- A repeatable check that says whether the reduced case still fails.
- Boundaries for what may be copied, edited, deleted, or shared.

## Procedure

1. Capture the unreduced failing case and the exact reducer check.
2. Split the case into removable units: files, fields, routes, flags, rows, fixtures, imports, dependency versions, or steps.
3. Remove or simplify one unit at a time, then rerun the reducer check.
4. Keep only removals that preserve the same failure signature.
5. Periodically revalidate that the reduced case still represents the original symptom.
6. Record the final minimal trigger and the smallest non-triggering control case.

## Route-Specific Fallbacks And Stop Conditions

- If the failure changes signature, restore the last valid reduced state and report the fork.
- If reduction needs destructive edits in source, use a disposable copy or stop for approval.
- If the check is flaky, route to `debugpro-flaky`.
- If the minimal trigger points to a specific state transition, route to `debugpro-root-cause-tracing`.
- Stop when further removal changes or hides the failure.

## Output Format

```markdown
## Delta Result
- Original repro:
- Reducer check:
- Minimal failing case:
- Passing control case:
- Removed safely:
- Failure signature preserved:
- Root-cause signal:
- Remaining noise:
```
