# Output Contracts

Match output to the task mode. Keep claims evidence-backed and separate confirmed defects from suspected risks.

## User Input Rounds

When DebugPro uses native `request_user_input` popup intake, include a `User input rounds` section in the output or handoff. Record each round's user-owned answers for symptom/impact, reproduction or evidence source, and safety boundary or desired next action. If the run proceeds with fewer than three user-owned answers, record the explicit exception and why evidence still supports the chosen route or stop condition.

## Finding Format

Use for review-only bug hunts:

```markdown
## Finding
- File/line:
- Severity:
- Failure path:
- Evidence:
- Fix:
- Verification needed:
```

If there are no confirmed findings, say what was reviewed and why no reportable defect was found.

## Fix Format

Use after implementation:

```markdown
## Fix Report
- Root cause:
- Fix:
- Adjacent sweep:
- Verification:
- Residual risk:
```

The root cause must name the earliest proven cause and why it produced the original symptom. The fix must explain why it addresses that cause instead of only masking the symptom.

## Production Incident Format

Use for telemetry-led incidents:

```markdown
## Production Debug Report
- Symptom/impact:
- Evidence checked:
- Timeline:
- Hypotheses:
- Cause:
- Containment:
- Fix:
- Verification:
- Residual risk:
```

Keep containment separate from root-cause repair.

## Confidence Levels

- High: reproduced or directly traced, fixed, and verified.
- Medium: traced from strong evidence but reproduction is partial or production-only.
- Low: plausible risk; do not present as a confirmed finding unless speculative leads were requested.
