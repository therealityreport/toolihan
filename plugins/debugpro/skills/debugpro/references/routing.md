# DebugPro Routing

Use this as the narrow matrix for choosing a DebugPro skill after intake.
For broad tool, connector, agent, or fallback selection, open `capability-router.md` first.
For method fan-out inside a chosen route, open `technique-index.md`.
For missing-evidence decisions, open `missing-evidence-routing.md`.
For parallel escalation, open `parallel-debugging-contract.md`.

## Skill Matrix

| Situation | Primary skill | Rule |
| --- | --- | --- |
| Symptom, impact, environment, reproduction, or evidence is missing | `debugpro-intake` plus `missing-evidence-routing.md` | Ask only for the smallest facts needed to route. |
| Cause is still unclear after intake | `debugpro-hypotheses` | Build 3-5 falsifiable hypotheses and probe one at a time. |
| Two or more independent read-only probes are justified | `debugpro-team` plus `parallel-debugging-contract.md` | Escalate only when the shared parallel gate passes. |
| Competing investigation reports exist | `debugpro-arbitration` | Compare confirmed, falsified, and inconclusive evidence before fixes. |
| Review-only bug hunt, diff audit, stack trace triage, or Sentry/log event triage | `debugpro-bug-hunt` | Report only evidence-backed defects and avoid edits unless a fix is approved. |
| Production or staging telemetry is the main evidence | `debugpro-production-debugging` | Lead with logs, traces, metrics, deploys, flags, and customer impact. |
| Source, package, cache, install, or runtime state may differ | `debugpro-source-runtime-parity` | Prove which copy is executing before editing. |
| Browser, localhost, UI, or rendered runtime behavior is the symptom | `debugpro-browser-runtime-proof` | Reproduce the visible/runtime signal and preserve logs or screenshots. |
| Frontend state, rendering, hydration, or client data flow is suspect | `debugpro-frontend-debugging` | Trace component, state, network, and browser console evidence together. |
| CI, PR checks, workflow config, or branch status failed | `debugpro-ci-pr-failure` | Start from the exact failing check, job, step, and commit. |
| MCP, plugin, connector, tool registration, or runtime ownership failed | `debugpro-mcp-runtime-ownership` | Separate configured, installed, exposed, and callable ownership. |
| macOS app build, signing, runtime, or desktop behavior failed | `debugpro-macos-debugging` | Tie source, bundle, logs, permissions, signing, and visible app state together. |
| Performance, latency, resource use, or throughput is the symptom | `debugpro-performance` | Measure before optimizing; keep a baseline and changed variable. |
| Regression window matters | `debugpro-bisect` | Use a repeatable signal and stop at the smallest supported window. |
| Minimal reproduction or input reduction is needed | `debugpro-delta` | Shrink inputs while preserving the failing signal. |
| Flaky behavior or order dependence is likely | `debugpro-flaky` | Capture seed, order, timing, pollution, and repeat counts. |
| More observability is needed before diagnosis | `debugpro-instrumentation` | Add temporary or durable signals only where they answer a hypothesis. |
| A fix is approved and original symptom must be rechecked | `debugpro-verify` | Verify the original failure first, then prevention. |
| A fix is approved and nearby same-surface defects may exist | `debugpro-adjacent-sweep` | Sweep only the touched surface and evidence-related neighbors. |

Use `evidence-modes.md` before `debugpro-bug-hunt`, `debugpro-ci-pr-failure`, or `debugpro-production-debugging` when the request starts from a diff, log, trace, stack, Sentry event, or static review surface.
Use `output-contracts.md` for review findings, fix reports, and production incident reports.
Use `secret-redaction.md` before quoting logs, traces, environment dumps, API failures, MCP diagnostics, proxy output, or browser/session artifacts.
Use `capability-router.md` before choosing a narrow skill when tool availability, connectors, MCPs, browser automation, editor diagnostics, docs drift, or optional agents affect the route.

## Tie-Breakers

- Browser-visible symptom, localhost rendering, profile state, console output, or network failure: start with `debugpro-browser-runtime-proof`.
- Frontend component state, hydration, routing, client data flow, or asset loading: start with `debugpro-frontend-debugging`.
- Measured latency, throughput, CPU, memory, resource use, query plans, or browser performance traces: start with `debugpro-performance`.
- MCP tool visibility, server startup, config ownership, exposed tools, auth, or callable status: start with `debugpro-mcp-runtime-ownership`.
- Source, package, installed runtime, cache, generated bundle, or plugin projection mismatch: start with `debugpro-source-runtime-parity`.
- Review-only diff, stack trace, log excerpt, Sentry event, or bounded static surface: start with `debugpro-bug-hunt`.
- Active production or staging impact with telemetry, deploy timeline, feature flags, users, logs, metrics, traces, or correlation IDs: start with `debugpro-production-debugging`.
- External docs uncertainty for a library, SDK, API, CLI, MCP, browser tool, framework, or cloud service: choose the symptom domain first, then use Context7 MCP for the docs question; use Context7 CLI only when a separate local CLI exists and MCP is unavailable.
- Editor diagnostics or active debug sessions: keep the symptom-domain route and use VS Code MCP as evidence, not as a separate route owner.
- Capability discovery, tool comparison, or route coverage maintenance: use `debugpro-source-runtime-parity` for source/cache/plugin state, or `debugpro-hypotheses` when the improvement target is unclear; use Tool Finder only for the discovery portion.
- Active debugging request that merely mentions tools: route by the failing symptom first, and do not run Tool Finder unless the user explicitly asks for tool discovery.

## Escalation Gate

Parallel or agent work is allowed only when `parallel-debugging-contract.md`
passes. This gate applies before `debugpro-team`,
Agent Teams, subagents, or parallel tool probes. If any gate answer is `No`,
stay single-threaded with `debugpro-hypotheses` or the current domain route. If
the request is mixed or tool-dependent, use `capability-router.md` before
escalation.

## Ambiguous Request Examples

| Request Shape | Route Rule |
| --- | --- |
| Browser-visible failure plus CI failure | Start with browser runtime proof; use CI only as secondary evidence until the visible signal is reproduced or ruled out. |
| MCP exposure failure plus source/cache drift | Start with MCP runtime ownership; use source/runtime parity to prove whether Codex is loading stale plugin files. |
| Production impact plus local console errors | Start with production debugging; use browser or frontend routes only after telemetry identifies the affected surface. |
| Flaky test plus possible external API change | Start with flaky isolation; do docs lookup after a repeatable signal exists. |
| DebugPro capability or routing improvement | Start with source/runtime parity when installed behavior must change; use hypotheses only if the desired routing change is unclear. |
| Active bug plus "what tools can help?" | Start with the owning DebugPro symptom route; treat Tool Finder as optional discovery only after direct evidence is bounded. |

## Stop Conditions

- The same workflow fails twice with the same substantive error and no new evidence.
- The next step is destructive, mutating, expensive, credential-bound, or permission-sensitive.
- Required logs, traces, credentials, runtime access, or reproduction data are missing.
- Concurrent edits make the target ownership ambiguous.

When stopped, report the exact blocker, collected evidence, and smallest decision needed.
