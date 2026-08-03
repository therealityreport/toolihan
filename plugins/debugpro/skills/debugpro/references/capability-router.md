# DebugPro Capability Router

## Purpose

Use this at the start of a broad, mixed, or tool-dependent `@debugpro` request.
It chooses the first evidence route, the useful capabilities, the fallback, and
the stop condition. It does not diagnose or fix the bug.

## How To Use This Router

1. Capture the symptom, impact, environment, exact error, reproduction path, and current evidence.
2. If existing source, log, test, or runtime evidence already proves the first route, do not prompt the user; route directly. Follow the user-level requesting-user-input contract only when the first route is ambiguous or required evidence is missing.
3. Choose one primary route from the use-case matrix; add secondary routes only when evidence requires it.
4. Open `routing.md` for the full skill matrix, then open only the domain references needed for that route.
5. Use capabilities only when they are available, relevant, and safe; otherwise use the listed fallback.
6. Label optional capabilities as `[available]`, `[optional]`, `[unavailable]`, or `[blocked]`.
7. Escalate to parallel work only when `parallel-debugging-contract.md` passes.
8. Stop before guessing, destructive edits, credential work, broad installs, or unclear ownership.

## Native Popup Intake

Prefer `user_questions`, then native `request_user_input`, only when the first route is ambiguous or evidence is missing after checking current source, logs, tests, runtime signals, and user-provided facts. The intake must ask for symptom/impact, reproduction or evidence source, and safety boundary or desired next action; add other independent material decisions to the same 4-6-question round without filler.

Require at least three user-owned answers for the popup intake path. If that is not possible, record an explicit exception naming the missing answer, why the route can still proceed or must stop, and the evidence-backed fallback. Any DebugPro output or handoff that used popup intake must include a `User input rounds` section.

## Use-Case Matrix

| Use case | Primary route | Capability bundle | Fallback |
| --- | --- | --- | --- |
| Missing symptom/evidence | `debugpro-intake` | shell inventory, logs, test output | Ask only for material missing facts. Follow the user-level structured-input fallback order only when the route is ambiguous or evidence is missing; do not prompt if source, log, test, or runtime evidence already proves the route. |
| Unclear root cause | `debugpro-hypotheses` | focused repro, logs, config/source search | Build 3-5 hypotheses and probe one at a time. |
| Independent hypotheses | `debugpro-team` | read-only parallel tracks plus arbitration | Stay single-threaded if any parallel gate is No. |
| Bug hunt, diff audit, or event triage | `debugpro-bug-hunt` | `git diff`, `rg`, logs, stack traces, Sentry events | Report evidence-backed defects only. |
| Browser localhost UI runtime failure | `debugpro-browser-runtime-proof` or `debugpro-frontend-debugging` | Browser, Chrome, Chrome DevTools MCP, Playwright, `curl` | Use HTTP checks, app logs, screenshots, and source inspection. |
| CI PR failure | `debugpro-ci-pr-failure` | GitHub MCP, `gh`, `inspect_pr_checks.py`, workflow logs | Inspect workflow files and reproduce locally. |
| MCP runtime ownership failure | `debugpro-mcp-runtime-ownership` | MCP Inspector, MCPJam, `mcp-debug`, `mcp-status`, config/process/log evidence | Compare config files, command lines, logs, and exposed tools. |
| Source runtime cache drift | `debugpro-source-runtime-parity` | `diff`, `cmp`, manifests, cache/source comparisons, sync dry run | Prove source state and report the missing runtime boundary. |
| Production staging incident | `debugpro-production-debugging` | deploy logs, traces, metrics, Sentry/Grafana/Datadog/Loki, cloud connectors | Bound from local config, deploy metadata, and provided excerpts. |
| Flaky tests | `debugpro-flaky` | repeat loops, seed/order capture, `find-polluter.sh` | Capture one failing seed/order and reduce the subset. |
| Regression window | `debugpro-bisect` | `git bisect`, focused failing command, change list | Compare candidate changes manually when checkout is unsafe. |
| Minimal repro needed | `debugpro-delta` | isolated script, fixture reduction, temp repro | Reduce the current fixture or command in place. |
| Performance issue | `debugpro-performance` | profilers, traces, flamegraphs, browser performance tools, timings | Add bounded timing probes or compare existing logs. |
| macOS app issue | `debugpro-macos-debugging` | Build macOS Apps, `xcodebuild`, unified logs, signing checks | Collect build output, bundle metadata, logs, and visible state. |
| External library API CLI uncertainty | selected domain route plus docs lookup | Context7 MCP first, official docs, version commands | Use official/local docs and cite uncertainty. |
| Fix approved and same surface may hide nearby bugs | `debugpro-adjacent-sweep` | same-surface source review, existing tests, narrow runtime checks | Do not broaden into a general review. |

## Skills

- Root and routing: `debugpro`, `debugpro-intake`, `debugpro-hypotheses`, `debugpro-root-cause-tracing`.
- Review and proof: `debugpro-bug-hunt`, `debugpro-source-runtime-parity`, `debugpro-browser-runtime-proof`, `debugpro-frontend-debugging`.
- Runtime domains: `debugpro-ci-pr-failure`, `debugpro-mcp-runtime-ownership`, `debugpro-macos-debugging`, `debugpro-performance`, `debugpro-production-debugging`.
- Isolation and completion: `debugpro-flaky`, `debugpro-bisect`, `debugpro-delta`, `debugpro-instrumentation`, `debugpro-verify`, `debugpro-adjacent-sweep`.
- Multi-track: `debugpro-team`, `debugpro-arbitration`.

## Agents

- `debugpro-capability-router`: returns a compact route packet for ambiguous or mixed-tool requests.
- `debugpro-investigator`: investigates exactly one read-only hypothesis or domain track.
- Agent Teams/subagents: optional only after the parallel contract passes and arbitration is planned.

## References

- Always useful: `routing.md`, `debugging-discipline.md`, `missing-evidence-routing.md`, `parallel-debugging-contract.md`.
- Domain references: `domain/browser-runtime-proof.md`, `domain/frontend-debugging.md`, `domain/ci-pr-failure.md`, `domain/mcp-runtime-ownership.md`, `domain/source-runtime-parity.md`, `domain/production-observability.md`, `domain/macos-debugging.md`.
- Report/proof references: `evidence-modes.md`, `output-contracts.md`, `secret-redaction.md`, `environment-diff.md`, `record-replay.md`, `strategy-catalog.md`, `technique-index.md`.
- `capability-integrations.md` is a compatibility pointer; this file owns the capability map.

## Tools And CLIs

- Source/runtime: `rg`, `find`, `ls`, `sed`, `diff`, `cmp`, manifests, lockfiles, install logs.
- HTTP/browser: `curl`, Browser, Chrome, Chrome DevTools MCP, Playwright, screenshots, console/network traces.
- CI: `gh`, `actionlint`, `act`, workflow logs, check logs, local failing commands.
- MCP: MCP Inspector, MCPJam, `mcp-debug`, `mcp-status`, config diffs, process evidence, exposed tool lists.
- macOS/performance: `xcodebuild`, unified logs, crash logs, `codesign`, `spctl`, profilers, timings, query plans.

## MCPs And Connectors

- Context7 MCP first for current docs; Context7 CLI only if separately installed and MCP is unavailable.
- GitHub MCP for PRs, Actions, annotations, changed files, and issues.
- VS Code MCP for diagnostics, symbols, and active debug sessions as evidence inside the owning route.
- Browser/Chrome/Chrome DevTools MCP for browser-visible proof.
- Render, Vercel, Cloudflare, Supabase, Sentry, Grafana, Datadog, and Loki only when credentials/scopes are available and the route needs them.
- Tool Finder is a maintenance and discovery aid, not a default debugging probe.

## Fallbacks

- Missing connector: use local config, logs, source, manifests, and user-provided evidence.
- Missing browser automation: use `curl`, app logs, supplied screenshots, and static inspection.
- Missing GitHub access: inspect workflow files and reproduce locally.
- Missing MCP tooling: compare config, process command lines, startup logs, and exposed tool lists.
- Missing production credentials: bound from deploy metadata, source config, and sanitized excerpts.
- Unsafe mutation or dirty ownership: stop and ask for the smallest safe decision.

## Tool Finder Use Rules

Use Tool Finder only when the user asks for tool, plugin, agent, skill, MCP, or
connector discovery, comparison, adoption, or DebugPro route maintenance. For
ordinary failures, route by the symptom first and do not list Tool Finder unless
discovery is explicitly part of the request. If it is secondary, label Tool
Finder as `[optional]` and keep direct evidence as the primary path.

## Capability Availability Labels

| Label | Meaning |
| --- | --- |
| `[available]` | Callable, installed, exposed, or present in the workspace. |
| `[optional]` | Helpful but not required for the first evidence loop. |
| `[unavailable]` | Missing or not exposed; use the fallback. |
| `[blocked]` | Present but missing credentials, profile state, access, or safe ownership. |

## Stop Conditions

- The same workflow fails twice with no new evidence gathered.
- Required credentials, logs, traces, browser access, production access, or repro access are missing.
- The next step is destructive, mutating, expensive, or permission-sensitive.
- Source/runtime/cache ownership is ambiguous or concurrent edits make it unsafe.
- Parallel tracks cannot stay independent or cannot be arbitrated before edits.

When stopped, report the blocker, evidence collected, unavailable capability,
safest fallback attempted, and smallest next decision needed.
