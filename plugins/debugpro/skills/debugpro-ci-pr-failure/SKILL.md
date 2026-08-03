---
name: debugpro-ci-pr-failure
description: Use when CI, PR checks, or GitHub Actions jobs fail.
---

# DebugPro CI PR Failure

Use this route to diagnose CI from the failing check evidence before changing code.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/ci-pr-failure.md`

## When To Use

- A PR check, GitHub Actions workflow, pipeline job, status check, or deployment check failed.
- CI passes locally but fails remotely, or remote CI has environment-only behavior.
- Workflow YAML, action versions, matrix values, secrets, permissions, caches, or artifacts may be involved.

## Evidence To Collect

- Repository, branch, PR, commit SHA, workflow name, job, step, run id, and check URL if available.
- Exact failing command, full error, stack trace, annotations, artifacts, and log window.
- Matrix values, runner OS, language/tool versions, cache hits, secrets/permission context, and changed files.
- Local reproduction command and whether it matches the CI job environment.
- Recent workflow, dependency, lockfile, and environment changes.

## First Probes

- Read the failing job log and isolate the first meaningful failure, not later cascading failures.
- Compare CI command, environment, versions, and working directory with local commands.
- Inspect workflow YAML, action pins, permissions, matrix, cache keys, and setup steps.
- Reproduce locally with the closest command; use `act` only when it matches enough of the runner context.
- Verify the fix against the failing command or the closest faithful local/remote check.

## Optional Tools, MCPs, And Connectors

- GitHub MCP or `gh` for PR checks, workflow logs, artifacts, annotations, and rerun metadata.
- `actionlint` for workflow syntax and policy mistakes.
- `act` for local workflow approximation when Docker and action support are suitable.
- Language/package CLIs for lockfile, version, and test reproduction.
- Context7 or official docs for current action, CLI, or platform behavior.

## Route-Specific Fallbacks

- If GitHub access is unavailable, use pasted logs, local workflow files, changed files, and the nearest local command.
- If logs are truncated, identify the missing section and avoid diagnosing from only cascade errors.
- If CI-only secrets or services are missing, prove the boundary and propose a minimal instrumentation or fixture path.

## Route-Specific Stop Conditions

- The next step requires rerunning expensive CI, changing secrets, broadening permissions, or mutating protected branches without approval.
- The first failing log section, workflow file, or runner context is unavailable.
- Multiple jobs fail for unrelated reasons and need separate routing.

## Output Format

```markdown
## CI PR Failure Report
- PR/commit/check:
- Failing workflow/job/step:
- First meaningful error:
- CI environment:
- Local reproduction:
- Cause:
- Fix:
- Verification:
- Unavailable evidence:
- Stop condition or residual risk:
```
