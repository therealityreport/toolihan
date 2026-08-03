# Evidence Modes

Use the narrowest mode that explains the request. Switch modes when the evidence changes.

## Diff Review

Use for branch changes, PRs, and local audits.

1. Identify base and changed files.
2. Read changed files plus only the callers, tests, schemas, migrations, and config needed to validate behavior.
3. Map touched inputs, external calls, persistence, auth, state transitions, async work, and error handling.
4. Report concrete failure paths, not style issues.
5. Confirm the issue is not already handled nearby or by tests.

Useful commands:

```bash
git status --short
git diff --stat <base>...HEAD
git diff --name-status <base>...HEAD
git diff <base>...HEAD -- <path>
```

## Failure Investigation

Use for failing tests, exceptions, logs, stack traces, Sentry issues/events, and user-reported broken behavior.

1. Preserve exact raw evidence: command output, error text, event id, route, stack trace, log lines, screenshots, metrics, or affected record.
2. Reproduce locally when practical. If not, identify the closest deterministic signal.
3. Trace backward from symptom to earliest wrong value, missing event, bad state transition, or failed dependency.
4. State hypotheses with confirming and falsifying evidence before editing.
5. Prefer tests, debugger inspection, focused queries, traces, replay data, or boundary logs.

## Sentry Or Production Event Triage

If Sentry evidence is available, extract:

- issue/event id, release, environment, timestamp, platform, transaction, route, frequency, first seen, last seen
- exception type, message, stack frames, culprit, breadcrumbs, tags, request context, replay/trace links
- release or deploy diff around first seen

Do not require Sentry access. If unavailable, use logs/tests/repro artifacts and mark production-only assumptions as unresolved.

## Static Bug Hunt

Use static inspection only as a supplement unless the defect is mechanically obvious. Good targets are changed validation, parsing, permissions, queries, migrations, async boundaries, duplicated logic near a proven bug, direct callers/tests, and nullable/empty/out-of-range data assumptions.
