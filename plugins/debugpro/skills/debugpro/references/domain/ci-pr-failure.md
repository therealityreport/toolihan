# CI And PR Failure

Use when a pull request, workflow, status check, action, branch rule, or hosted
build fails.

## Evidence To Capture

- Repository, PR/commit SHA, branch, workflow, job, step, and runner image.
- Exact failing command and error excerpt.
- Diff between local and CI environment: versions, env vars, secrets availability, paths.
- Workflow file and action versions.
- Whether the failure reproduces locally with the same command.

## First Probes

- Read the failing job before changing source.
- Separate test failure, workflow syntax, dependency install, secret/config, and runner drift.
- Use local `actionlint` or equivalent only when workflow syntax is suspect.
- Use `act` only when the workflow is safe and local emulation matches the needed signal.

## Stop Conditions

- Logs are unavailable or redacted enough to hide the failing command.
- Fix would require changing branch protection, secrets, or paid CI settings.
- Local reproduction cannot match the runner and the conclusion would be guesswork.

## Handoff Line

`CI proof: workflow=<name>, job=<name>, step=<name>, sha=<sha>, error=<summary>.`
