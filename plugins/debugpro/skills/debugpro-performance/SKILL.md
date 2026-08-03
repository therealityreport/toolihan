---
name: debugpro-performance
description: Use when slowness, resource use, throughput, or latency needs measurement.
---

# DebugPro Performance

Use this technique when the failure is about speed, responsiveness, resource pressure, throughput, latency, memory, CPU, IO, network, or scaling.

References: `../debugpro/references/capability-router.md`, `../debugpro/references/technique-index.md`, `../debugpro/references/debugging-discipline.md`.

## When To Use

- A workflow is slow, stalls, times out, leaks memory, burns CPU, or regresses under load.
- The user has a performance target or a before/after regression.
- Profiling, traces, metrics, or controlled benchmarks can identify the bottleneck.

## Required Setup And Evidence

- Performance symptom, target, and impact.
- Repro workload, input size, environment, and version.
- Baseline measurement with command, duration, resource stats, and variance.
- Relevant logs, traces, profiles, metrics, browser performance data, or flamegraphs.
- Recent changes and known environmental differences.

## Procedure

1. Define the metric: latency, throughput, CPU, memory, IO, network, render time, bundle size, or error budget.
2. Capture a baseline with enough repeated runs to understand variance.
3. Profile the hottest path under the same workload.
4. Identify the dominant bottleneck before changing code.
5. Apply the smallest fix to the measured bottleneck.
6. Re-measure the same workload and report before/after deltas.

## Route-Specific Fallbacks And Stop Conditions

- If measurements are noisy, stabilize the workload before diagnosing.
- If the issue is browser/UI-specific, use browser performance tools when available.
- If the issue is production-only, route through `debugpro-production-debugging`.
- Stop before speculative optimization when no measured bottleneck exists.
- Stop if the proposed optimization changes behavior without correctness proof.

## Output Format

```markdown
## Performance Result
- Symptom:
- Metric and target:
- Baseline:
- Profile evidence:
- Bottleneck:
- Fix:
- After measurement:
- Delta:
- Remaining constraints:
```
