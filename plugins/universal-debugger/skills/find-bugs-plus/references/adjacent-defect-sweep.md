# Adjacent Defect Sweep

Run this when the user asked for fixes and you are already editing a proven bug. Catch same-family defects while context is loaded; do not turn a focused repair into an unbounded refactor.

## Sweep Scope

Search only:

- the same function, component, endpoint, job, parser, query, migration, or config surface
- direct callers/callees needed to validate the proven contract
- tests or fixtures covering that surface
- duplicated code paths with the same input shape or guard condition
- release, deploy, or config paths directly implicated by the symptom

Stop before touching unrelated features, unrelated files, broad style cleanup, or speculative improvements.

## Search Prompts

Ask these while fixing:

1. Does this root cause appear in sibling branches, callers, duplicated validators, or mirrored client/server code?
2. Did the failing input shape expose a missing guard that other entry points also lack?
3. Is the test only covering the exact case, or should the same contract be asserted at the shared boundary?
4. Did the fix change a shared helper, schema, migration, or data contract that requires focused follow-through?
5. Is there an adjacent bug that can be verified by the same failing test family or one small additional test?

## Fix Rules

Fix an adjacent defect only when all are true:

- it is in the sweep scope above
- it shares the same root cause, contract, or validation path
- the change is small and does not obscure the primary fix
- verification is available now
- the final report separates primary fix from adjacent fixes

Otherwise report it as a follow-up with evidence and do not edit it.

## Report Shape

```text
Primary bug fixed:
- Evidence:
- Verification:

Adjacent defects checked:
- <surface>: clean | fixed | follow-up | not checked

Adjacent fixes made:
- <file:line> - <same-family defect and verification>

Follow-ups:
- <evidence-backed item that was out of scope or unverified>
```
