# Runtime verification and CI diagnosis

## Runtime mode

Use runtime [scope] only when static code cannot prove the behavior. State the named runtime surface before inspecting it.

Allowed without additional mutation permission:

- Read logs and deployment status
- Inspect browser layout, console, network, accessibility, and storage without submitting forms
- Send GET, HEAD, or documented read-only requests
- Read deployed configuration with secret values redacted
- Run database SELECT or equivalent read-only queries

Require explicit authorization before form submissions, state-changing requests, database writes, restarts, deployments, queue operations, cache flushes, or configuration changes.

Use deep_debugger for normal runtime investigation and risk_owner for cross-system or high-consequence failures. Have a separate adversarial_reviewer evaluate the evidence. Record:

- Surface, environment, and timestamp
- Read-only action taken
- Sanitized observation
- Code or configuration path it confirms or disproves
- Remaining uncertainty

Persist summaries, not raw sensitive logs, cookies, tokens, or full database rows.

If required tooling or access is absent, name the missing capability and provide a safe manual evidence request. Do not infer a live result from source code.

## CI mode

For ci [check-or-run]:

1. Resolve the named check or run, or current branch failures.
2. Capture provider, commit, failing job or step, exact command, error, relevant stack trace, and environment differences.
3. Use repository_mapper to map changed files and the smallest owning code path.
4. Reproduce locally only with non-destructive commands when feasible.
5. Separate branch-introduced, pre-existing, flaky, and infrastructure failures.
6. Use deep_debugger for infrastructure or concurrency causes and an adversarial_reviewer for causal judgment.
7. Write a focused repair plan; do not broaden into a repository audit.

After the same command fails twice with the same substantive error, stop retrying. Preserve the exact evidence, research current primary sources when third-party behavior is involved, and rank plausible causes before planning the smallest fix.

If remote CI evidence is unavailable, produce grounded local reproduction steps and list the missing data. Never guess the remote failure.
