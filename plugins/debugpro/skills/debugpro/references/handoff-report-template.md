# DebugPro Handoff Report Template

Use this compact format for final debugging reports, arbitration results, or
handoffs to another agent. Keep claims tied to evidence.

```markdown
Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED

## Root Cause Or Current Boundary
State the supported cause. If not fully proven, state what is bounded and what remains unknown.

## Evidence
- `path:line` or source: observed fact and why it matters.
- Command/log/trace/test/UI signal: observed output and implication.

## User input rounds
Include this section only if native `request_user_input` popup intake was used. Record symptom/impact, reproduction or evidence source, safety boundary or desired next action, and any explicit exception for fewer than three user-owned answers.

## Failing Signal
Describe the smallest command, route, event, log query, trace, screenshot, or metric that demonstrates the issue.

## Change Or Recommendation
Describe the practical change first. Then list changed files or code paths.

## Verification
- Command/evidence source: pass/fail and important output.
- Original symptom: fixed, still failing, or not rechecked with reason.

## Prevention
List tests, assertions, monitoring, alerts, docs, or runbook updates that fit the codebase.

## Adjacent Sweep
State whether a same-surface sweep ran, what boundary it covered, and any related findings.

## Open Questions
List only decisions or missing evidence that could change the conclusion.
```
