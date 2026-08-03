---
name: debugpro-verify
description: Use when a candidate fix needs verification against the original failing signal before declaring completion.
---

# DebugPro Verify

Use this technique after a cause-backed fix exists and the goal is to prove the outcome against the original symptom and acceptance criteria.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`.

## When To Use

- A fix has been made or selected and needs evidence of resolution.
- The original failure had a specific command, workflow, log, UI state, or production signal.
- The user needs a clear done/not-done report.

## Required Setup And Evidence

- Original symptom and exact reproduction path.
- The cause and fix summary.
- Required checks: tests, commands, logs, UI/runtime proof, data checks, or deployment signals.
- Known limitations and unchanged out-of-scope areas.
- Any flaky behavior that requires repeated confirmation.

## Procedure

1. Re-run the original failing check first.
2. Run the narrow regression checks that cover the changed boundary.
3. Check any user-visible, runtime, or data surface that was part of the original failure.
4. Compare before/after evidence without overstating coverage.
5. If a check fails, stop and route back to the relevant diagnostic skill.
6. Report exact commands, results, unresolved risks, and unsupported claims.

## Route-Specific Fallbacks And Stop Conditions

- If the original repro is unavailable, use the closest evidence-backed substitute and label the gap.
- If verification is flaky, route to `debugpro-flaky`.
- If runtime proof is needed and unavailable, state the blocker instead of claiming completion.
- Stop when required checks pass, fail, or are blocked with concrete reason.

## Output Format

```markdown
## Verification
- Original symptom:
- Fix under verification:
- Checks run:
- Results:
- Runtime/user-visible proof:
- Remaining gaps:
- Status: PASS | FAIL | BLOCKED | PARTIAL
```
