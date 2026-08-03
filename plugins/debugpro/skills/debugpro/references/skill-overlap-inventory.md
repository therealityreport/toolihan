# DebugPro Skill Overlap Inventory

This inventory separates useful overlap from boilerplate that belongs in shared
references.

## Shared References

- `debugging-discipline.md`: global evidence, probe, fallback, stop, fix, and
  verification contract.
- `parallel-debugging-contract.md`: shared track, safety, investigator, and
  arbitration contract for parallel debugging skills.
- `missing-evidence-routing.md`: decision table for incomplete evidence cases.

## Consolidated Boilerplate

Shared references now own these repeated rules:

- Start from the original failing signal.
- Capture expected behavior, actual behavior, environment, ownership boundary,
  relevant paths, recent changes, and safety constraints.
- Prefer the smallest confirming or falsifying probe.
- Record commands, inputs, outputs, paths, and runtime surfaces.
- Stop after two same-error retries with no new evidence.
- State unavailable tools, credentials, runtime surfaces, or logs.
- Stop before destructive cleanup, global config edits, production mutation,
  credential changes, broad rewrites, or expensive external actions.
- Verify against the original failing signal before claiming completion.

## Overlap Groups

### Evidence-First Technique Skeleton

Skills:

- `debugpro-bisect`
- `debugpro-delta`
- `debugpro-flaky`
- `debugpro-instrumentation`
- `debugpro-performance`
- `debugpro-root-cause-tracing`
- `debugpro-verify`

Policy:

- Keep the repeated section shape because it makes technique skills scannable.
- Move only generic safety and evidence rules to `debugging-discipline.md`.
- Preserve route-specific evidence lists and output fields.

### Runtime Evidence Routes

Skills:

- `debugpro-browser-runtime-proof`
- `debugpro-frontend-debugging`
- `debugpro-source-runtime-parity`
- `debugpro-macos-debugging`
- `debugpro-mcp-runtime-ownership`

Policy:

- Keep route-specific path, process, browser, CI, MCP, macOS, and runtime probes.
- Use `debugging-discipline.md` for generic retry, fallback, mutation, and
  verification rules.

### Parallel Investigation And Arbitration

Skills:

- `debugpro-team`
- `debugpro-arbitration`

Policy:

- Use `parallel-debugging-contract.md` for the safety gate, track packet,
  investigator report, and arbitration-before-fix rule.
- Use `debugpro-team` as the single coordination entrypoint and
  `debugpro-arbitration` for the final evidence decision.

### Missing Context And Hypothesis Formation

Skills:

- `debugpro-intake`
- `debugpro-hypotheses`
- `debugpro-root-cause-tracing`
- `debugpro-instrumentation`

Policy:

- Use `missing-evidence-routing.md` to choose among these skills.
- Do not merge them: each owns a different stage of the evidence lifecycle.

## Current Rule

Do not remove route-specific evidence lists just to make the skills shorter.
Only move text when it is generic across routes and does not affect debugging
behavior.
