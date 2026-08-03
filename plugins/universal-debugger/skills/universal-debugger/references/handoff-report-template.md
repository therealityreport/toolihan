# Handoff Report Template

Use this format when reporting a diagnosis, handing work to another debugging skill, or leaving an issue for a reviewer. Every claim should be backed by evidence or labeled as unresolved.

```text
Root Cause
- The earliest proven cause and causal chain from source to symptom.

Evidence
- Reproduction, command output, failing test, logs, traces, file references, queries, screenshots, or metrics that support the cause.
- Evidence that ruled out major competing hypotheses.

Minimal Reproduction or Failing Test
- Exact steps, command, fixture, request, URL, test name, or reason a reproduction is blocked.

Fix
- Minimal change made or proposed.
- Why it addresses the proven source instead of only the symptom.

Prevention
- Test, assertion, validation, monitor, alert, clearer error, migration guard, or documentation update that reduces recurrence.

Open Questions
- Missing access, context, logs, tests, data, approvals, or unresolved hypotheses.
```

## Validation Checklist

- The original symptom was reproduced or the reproduction blocker is explicit.
- Root cause is supported by cited evidence.
- Competing hypotheses were ruled out or marked inconclusive.
- Only one fix path is proposed at a time.
- The fix was verified against the original symptom when implementation occurred.
- Temporary probes or logs were removed, or retained observability is intentional.
- Residual risk is stated in concrete terms.

## Residual Risk Language

Use direct language:

- "Residual risk is low because the failing test now passes and the original command was rerun."
- "Residual risk remains around production-only data because local reproduction used a fixture."
- "Blocked: root cause is not proven until the missing log or environment value is available."

Do not write a confident handoff when the evidence is partial. State the uncertainty and the next artifact needed.
