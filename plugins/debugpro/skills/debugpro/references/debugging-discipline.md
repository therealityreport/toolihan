# DebugPro Shared Discipline

Use this reference when a DebugPro route needs shared guardrails without copying
them into every skill.

## Shared Execution Contract

Every DebugPro skill follows this contract unless a route-specific section
narrows it further.

### Required Setup

- Start from the original failing signal: command, test, log, trace, route,
  visible UI state, metric, report, or user-provided repro.
- Capture expected behavior, actual behavior, environment, ownership boundary,
  relevant paths, recent changes, and safety constraints.
- Preserve user work and mutable runtime state. Do not overwrite source, reset
  caches, clear data, rotate secrets, or mutate global config without approval.

### Probe Rules

- Prefer the smallest probe that can confirm or falsify the current claim.
- Change one variable at a time and record the command, input, output, timestamp,
  path, and runtime surface used.
- If source and runtime disagree, prove ownership before editing and route to
  `debugpro-source-runtime-parity` when needed.
- If evidence is missing at the deciding boundary, route to
  `debugpro-instrumentation` instead of guessing.

### Shared Fallbacks

- If a preferred tool, connector, browser bridge, runtime surface, or credential
  is unavailable, state the missing surface and use the nearest evidence-backed
  substitute.
- If the same workflow fails twice with the same substantive error and no new
  signal, stop retrying and report the exact command, error, logs, and next
  evidence source.
- If multiple independent hypotheses remain, route to `debugpro-hypotheses` or
  `debugpro-team` before making a fix.

### Shared Stop Conditions

- Stop before destructive cleanup, broad rewrites, production mutation, global
  config edits, credential changes, or expensive external actions unless the
  user explicitly approves that step.
- Stop when the first wrong boundary is proven, the current hypothesis is
  falsified, or the next required evidence source is unavailable.
- Do not claim completion until the original failing signal, or the closest
  labeled substitute, has been checked.

### Shared Output Fields

Every DebugPro result should include:

- original symptom and expected behavior;
- evidence collected, including unavailable evidence;
- root cause or current hypothesis status;
- false leads ruled out or remaining alternatives;
- smallest fix, next probe, or stop reason;
- verification against the original signal or a clearly labeled gap.

## Evidence Strength

- Strong: reproducible command, failing test, source path, trace span, log event, metric, database/API state, or visible UI signal tied to the symptom.
- Medium: correlation with deploys, config changes, timing, data cohorts, warnings, or resource pressure.
- Weak: assumption, anecdote, broad pattern match, or absence of a search result.

Prefer strong evidence. Label medium or weak evidence clearly when it is the best
available signal.

## Evidence Loop

1. State the observed symptom and original failing signal.
2. Capture environment, version, inputs, recent changes, and ownership boundary.
3. Form a falsifiable hypothesis only when the cause is not already proven.
4. Run the smallest probe that can confirm or falsify the hypothesis.
5. Fix only after the evidence supports the cause.
6. Verify against the original signal before claiming completion.

## Parallel Gate

Parallel investigation is escalation. Use it only when each track has an
independent probe, read-only or non-overlapping ownership, and one arbitration
step before edits.

## Fix Gate

Apply a fix only when evidence confirms or strongly supports the cause. If the
next step is destructive, mutating, expensive, credential-bound, or ambiguous,
stop and report the smallest decision needed.

## Verification Gate

Verify the original failing signal first. Add prevention only where the project
has a real surface for it: test, assertion, monitor, alert, runbook, or validation
check.
