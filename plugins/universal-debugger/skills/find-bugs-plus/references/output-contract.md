# Output Contract

Match output to the task mode. Keep claims evidence-backed and separate confirmed defects from suspected risks.

## Finding Format

Use for review-only bug hunts:

```text
Finding
- File:Line:
- Severity:
- Failure path:
- Evidence:
- Fix:
- Verification needed:
```

If there are no confirmed findings, say what was reviewed and why no reportable defect was found.

## Fix Format

Use after implementation:

```text
Root cause:
- Earliest proven cause and why it produced the symptom.

Fix:
- Minimal change made.
- Why it addresses the cause instead of only the symptom.

Adjacent sweep:
- Related surfaces checked.
- Adjacent fixes made or follow-ups left.

Verification:
- Commands, tests, repro steps, traces, logs, or blockers.

Residual risk:
- Concrete remaining uncertainty, if any.
```

## Confidence Levels

- High: reproduced or directly traced, fixed, and verified.
- Medium: traced from strong evidence but reproduction is partial or production-only.
- Low: plausible risk; do not present as a finding unless speculative leads were requested.
