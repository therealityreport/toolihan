---
name: debugpro-bisect
description: Use when a regression needs an evidence-backed first bad change.
---

# DebugPro Bisect

Use this technique when the symptom is reproducible and there is a known or likely good state before the failure.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`.

## When To Use

- A focused command, test, log check, or UI probe can classify a state as good or bad.
- The suspected change range is too large to inspect manually.
- The goal is to identify the first bad commit, version, config change, migration, dependency update, or feature flag.

## Required Setup And Evidence

- Exact symptom and expected behavior.
- Known bad state and best available known good state.
- Deterministic classifier command with clear pass/fail output.
- Current worktree and runtime state, including uncommitted edits that must not be overwritten.
- Any required env vars, fixtures, services, seeds, or cache state.

## Procedure

1. Restate the regression range, classifier command, and safety boundary.
2. Confirm the classifier fails at the bad state and passes at the good state.
3. Use the narrowest safe bisect mechanism available: `git bisect`, dependency version binary search, config toggles, feature flags, or fixture reduction.
4. Record each tested state, command, result, and notable environmental difference.
5. When a first bad state is found, inspect the change and map it to the failing symptom.
6. Stop at the smallest evidence-backed culprit; do not broaden into cleanup.

## Route-Specific Fallbacks And Stop Conditions

- If the worktree is dirty and cannot be protected, stop before changing refs.
- If the classifier is flaky, route to `debugpro-flaky` before bisecting.
- If no known good state exists, route to `debugpro-hypotheses` or `debugpro-root-cause-tracing`.
- If setup cost makes full bisect unsafe, test a short suspected change list and report the limitation.
- Stop when the first bad state is identified or when evidence shows the range/classifier is invalid.

## Output Format

```markdown
## Bisect Result
- Symptom:
- Good state:
- Bad state:
- Classifier:
- States tested:
- First bad state:
- Evidence:
- Root-cause link:
- Fix direction:
- Unresolved limits:
```
