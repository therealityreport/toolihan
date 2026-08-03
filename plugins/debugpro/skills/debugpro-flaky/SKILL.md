---
name: debugpro-flaky
description: Use when tests fail by seed, timing, order, or pollution.
---

# DebugPro Flaky

Use this technique when the same command sometimes passes and sometimes fails, or when failures depend on order, timing, resources, seed, or shared state.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`.

## When To Use

- A test, CI job, UI flow, service check, or script is intermittent.
- The failure appears only after another test or command runs first.
- Logs suggest timing, retries, shared temp files, leaked env, database state, network state, or resource contention.

## Required Setup And Evidence

- Exact command or workflow, including CI/local environment differences.
- Pass/fail counts from repeated runs.
- Seeds, randomization flags, worker counts, test order, timing, and resource limits.
- Logs from at least one pass and one fail when feasible.
- Any suspected polluter command or test order list.

## Procedure

1. Reproduce the flake with repeated runs and capture the failure signature.
2. Separate categories: randomness, timing, test order, shared state, external dependency, resource pressure, or runtime drift.
3. Run the target in isolation, then with lower concurrency and fixed seed when supported.
4. If order is suspected, use `scripts/find-polluter.sh` with explicit candidate commands.
5. Compare pass and fail evidence before changing code.
6. Fix the proved leak, race, timeout, randomness, isolation gap, or environment drift.

## Helper

```bash
skills/debugpro-flaky/scripts/find-polluter.sh --runs 20 -- "your test command"
skills/debugpro-flaky/scripts/find-polluter.sh --runs 10 --candidates suspects.txt -- "your target test"
```

The helper only executes commands provided by the user. It does not modify source files, reset state, or infer cleanup.

## Route-Specific Fallbacks And Stop Conditions

- If the failure cannot be reproduced after a reasonable repeat loop, report the measured confidence and needed trigger.
- If every failure has a different signature, return to `debugpro-hypotheses`.
- If the target requires external services that are unstable, isolate service health before blaming code.
- Stop before destructive cleanup, database resets, or cache deletion unless approved for the environment.

## Output Format

```markdown
## Flaky Result
- Target:
- Failure signature:
- Reproduction rate:
- Variables controlled:
- Polluter/order evidence:
- Root cause:
- Fix:
- Verification loop:
- Remaining risk:
```
