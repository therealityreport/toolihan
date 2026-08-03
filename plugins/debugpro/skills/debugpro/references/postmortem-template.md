# DebugPro Postmortem Template

Use after an incident or high-impact regression when the user wants prevention,
not just a fix summary.

```markdown
# Postmortem: <incident name>

## Impact
- User/customer/system impact:
- Start:
- End:
- Severity:

## Root Cause
State the evidence-supported cause in one paragraph.

## Timeline
- Time: observed event, source, and implication.

## Detection
- First signal:
- Missed or delayed signals:
- Strongest evidence source:

## Resolution
- Change made:
- Why it addressed the cause:
- Verification against original signal:

## Contributing Factors
- Factor:
- Evidence:

## Prevention
- Code or config hardening:
- Test or validation:
- Monitoring or alert:
- Runbook or ownership update:

## Follow-Up Decisions
- Decision needed:
- Owner:
- Deadline or trigger:
```
