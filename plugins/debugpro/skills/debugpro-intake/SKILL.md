---
name: debugpro-intake
description: Use when a debugging request lacks facts needed for safe diagnosis.
---

# DebugPro Intake

Collect minimum facts before diagnosis. Preserve exact errors, casing, ids, and command output.
Use `../debugpro/references/missing-evidence-routing.md` when missing evidence
could route to several different debugging skills.

## Native Popup Intake Gate

Follow the user-level requesting-user-input contract. Prefer `user_questions` when available and fall back to native `request_user_input`. Use structured intake only when the first DebugPro route is ambiguous or required evidence is missing. Do not prompt when existing source, log, test, or runtime evidence already proves the route.

The first intake must ask for these three user-owned answers:

- Symptom/impact.
- Reproduction or evidence source.
- Safety boundary or desired next action.

Include other already-known, independent decisions in the same 4-6-question `user_questions` round when material; do not create filler questions. Require at least the three core user-owned answers for this intake path before diagnosis. If fewer than three answers are available, proceed only when an explicit exception is recorded with the missing answer, reason, and safest route boundary.

Record every popup round in the final intake output or handoff under `User input rounds`.

## Intake Checklist

- Symptom and impact.
- Reproduction or nearest signal.
- Expected versus actual behavior.
- Environment and recent changes.
- Suspected scope.
- Evidence sources checked or missing.
- Exact error text.
- Popup intake answers, when used.

## Output

End intake with:

```markdown
## Debug Intake
- Symptom:
- Impact:
- Reproduction or nearest signal:
- Expected:
- Actual:
- Environment:
- Recent changes:
- Scope:
- Evidence available:
- Exact error text:
- Missing facts:
- Next route:

## User input rounds
- Round 1:
  - Symptom/impact:
  - Reproduction or evidence source:
  - Safety boundary or desired next action:
  - Exception recorded, if fewer than three answers:
```

Route through `../debugpro/references/capability-router.md` when the next owner depends on browser, CI, MCP, production, source/runtime, or other tool availability. Otherwise use `../debugpro/references/missing-evidence-routing.md` to choose `debugpro-hypotheses`, `debugpro-root-cause-tracing`, `debugpro-instrumentation`, or the closest domain route.
