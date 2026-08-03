# Debugging Operating Model

Use this model when the issue crosses stacks or starts with incomplete context. The model is universal in shape, not in evidence access: any codebase can begin here, but real diagnosis still depends on access to the relevant code, reproduction signal, logs, tests, traces, data, environment, and recent-change context.

## Issue Intake

Capture these fields before committing to a fix path:

- Symptom: exact error, broken behavior, or observed anomaly.
- Reproduction: deterministic steps, failing command, fixture, URL, request payload, job id, user action, or closest repeatable signal.
- Expected versus actual behavior.
- Environment: repository/app, runtime, dependency versions, operating system, browser/device, service, deploy target, credentials boundary, data source.
- Recent changes: commits, migrations, dependency updates, config or secret changes, deploys, data imports, feature flags.
- Scope: first seen, frequency, affected users/records/routes/platforms, known-good comparison.
- Evidence inventory: logs, tests, traces, screenshots, metrics, database rows, stack traces, command output.

If any field is unavailable, say whether investigation can continue with reduced confidence or is blocked until the user supplies it.

## Root-Cause-First Loop

1. Reproduce the original symptom or identify the closest observable signal.
2. Preserve the raw failure text and relevant context before interpreting it.
3. Establish a known-good path, contract, baseline, or prior behavior.
4. Trace backward from the visible symptom to the earliest incorrect value, missing event, bad state transition, or failed dependency.
5. For non-obvious causes, list falsifiable hypotheses and expected probe results.
6. Run one targeted probe at a time. Prefer tests, traces, debugger inspection, focused queries, or boundary logs.
7. Confirm the causal chain before editing production code.
8. Make one minimal fix for the proven source.
9. Before final verification, search the same touched surface for adjacent defects that share the same root cause, contract, guard, data shape, or validation path.
10. Fix adjacent defects only when they are small, same-family, and verifiable by the current test or one targeted additional check. Otherwise report them as follow-ups.
11. Verify the original reproduction, each adjacent fix, and any prevention coverage.
12. Remove temporary instrumentation or mark intentionally retained observability.

## Stop Rules

Stop and return to investigation when:

- a proposed fix relies on "probably" instead of evidence
- a change would alter multiple variables at once
- a probe is too broad to distinguish hypotheses
- a fix fails and the result has not been recorded
- three fixes have failed
- the symptom changes and no longer matches the original reproduction
- missing access, data, logs, tests, or environment details make the next claim speculative

After a failed fix, record what it disproved before trying another path.

## Adjacent Bug Search During Fixes

When the user asked for implementation, the repair pipeline includes a bounded same-family bug search. Check direct siblings, callers, duplicated guards, mirrored client/server contracts, tests, fixtures, and release/config paths implicated by the proven root cause. This is not permission for broad cleanup. If the adjacent defect is unrelated, unverified, or would make the primary fix harder to review, leave an evidence-backed follow-up instead of editing it.

## Instrumentation Boundaries

Use targeted instrumentation at boundaries that can distinguish hypotheses. Avoid broad log spam, noisy dumps, or adding logs across the whole codebase. Temporary logs should be easy to find and remove. Prefer existing debuggers, profilers, tests, traces, replay tools, and structured queries when they can answer the question directly.

## Cross-Codebase Constraints

"Any codebase" means the workflow can start in any stack or repo. It does not mean the plugin can diagnose without the necessary evidence. When access or signals are missing, the correct result is a bounded handoff or a request for the missing artifact, not a guessed fix.
