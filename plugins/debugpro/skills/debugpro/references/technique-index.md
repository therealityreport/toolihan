# DebugPro Technique Index

Use this after `capability-router.md` has selected a route and `routing.md` has
chosen the DebugPro skill family. This file fans out to debugging methods, not
tool ownership.

## Method Matrix

| Need | Technique | Evidence to keep |
| --- | --- | --- |
| Unclear cause | Hypothesis tracing | Hypothesis, probe, result, next implication. |
| Unknown regression window | Bisect | Known-good, known-bad, command, first bad change. |
| Oversized failing case | Delta reduction | Original input, reduced input, preserved failure. |
| Flaky or order-dependent failure | Repeat and polluter search | Seed, order, count, timing, isolation result. |
| Runtime differs from source | Source/runtime parity | Executing path, built artifact, cache, version, process. |
| Browser/UI issue | Runtime proof | URL, viewport, console, network, screenshot, app logs. |
| Production incident | Observability timeline | Impact, deploys, flags, logs, traces, metrics. |
| Performance issue | Baseline and profiling | Baseline, changed variable, profile, resource metric. |
| Missing signal | Instrumentation | Question answered, added signal, removal/durability plan. |
| After fix | Verification | Original failing signal, prevention signal, residual risk. |

## Fast Choice Rules

- Use `strategy-catalog.md` for selecting the investigation pattern.
- Use `evidence-catalog.md` for deciding which signals are strong enough.
- Use `bug-patterns.md` for common failure shapes.
- Use `defense-patterns.md` for prevention after the fix.
- Use `environment-diff.md` when the same code behaves differently across machines, branches, profiles, or deploys.
- Use `record-replay.md` when timing, ordering, UI, network, or data replay matters.
- Use `forensics.md` when evidence may disappear or multiple actors changed state.

## Stop Rule

If a technique cannot preserve or improve evidence, do not keep running it. Return
to the chosen route and report the blocker.
