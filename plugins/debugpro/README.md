# DebugPro

DebugPro is a local Codex plugin for evidence-first debugging. It routes failures through a small evidence loop first, then selects the right skill, agent, reference, tool, CLI, MCP, connector, fallback, and stop condition before diagnosis or edits.

## Routing Model

DebugPro uses two routing layers:

- Capability routing: `skills/debugpro/references/capability-router.md` decides the useful capability bundle for a broad or mixed `@debugpro` request. It covers skills, agents, references, tools, CLIs, MCPs, connectors, fallbacks, and stop conditions.
- Capability integrations: `skills/debugpro/references/capability-integrations.md` is a compatibility pointer to the canonical capability router.
- Skill routing: `skills/debugpro/references/routing.md` picks the specific DebugPro skill once the failure family is known.
- Technique indexing: `skills/debugpro/references/technique-index.md` explains method choices such as bisecting, delta debugging, instrumentation, verification, and flaky-test isolation.
- Evidence modes and output contracts: `skills/debugpro/references/evidence-modes.md` and `skills/debugpro/references/output-contracts.md` separate diff review, failure investigation, event triage, bug hunting, implementation, and incident reports.
- Secret redaction: `skills/debugpro/references/secret-redaction.md` keeps logs, traces, env dumps, API errors, MCP diagnostics, and proxy output safe to quote.
- Missing-evidence routing: `skills/debugpro/references/missing-evidence-routing.md` chooses intake, hypotheses, root-cause tracing, instrumentation, or a domain route when the blocker is incomplete evidence.
- Parallel debugging contract: `skills/debugpro/references/parallel-debugging-contract.md` owns the shared track, safety, investigator, and arbitration rules for `debugpro-team` and `debugpro-arbitration`.
- Overlap inventory: `skills/debugpro/references/skill-overlap-inventory.md` records which overlapping language is intentional and which belongs in shared references.
- Shared evidence: `skills/debugpro/references/shared-evidence-contract.md` defines the `shared-evidence.v1.json` package used to exchange sourced findings with Plan Grader and other review/debugging plugins without re-parsing Markdown.

Use `agents/debugpro-capability-router.md` when the first route is ambiguous, multi-signal, or depends on optional tooling. Use `agents/debugpro-investigator.md` after routing when one hypothesis needs read-only investigation.

Follow the user-level requesting-user-input contract. Prefer `user_questions`, fall back to native `request_user_input`, and prompt only when the first route is ambiguous or required evidence is missing. Collect symptom/impact, reproduction or evidence source, and safety boundary or desired next action; include other independent material decisions in the same 4-6-question round without inventing filler. Do not prompt when existing source, log, test, or runtime evidence already proves the route. Record structured answers in DebugPro output or handoff under `User input rounds`.

## Skills

- `debugpro`: root router for active failures, failed tests, regressions, logs, traces, incidents, and ambiguous root-cause work.
- `debugpro-intake`: captures missing debugging facts before diagnosis.
- `debugpro-hypotheses`: generates falsifiable debugging hypotheses.
- `debugpro-arbitration`: compares hypothesis results before fixes.
- `debugpro-production-debugging`: treats production logs, traces, events, deploys, metrics, and flags as evidence.
- `debugpro-adjacent-sweep`: bounds same-surface adjacent checks after an approved fix.
- `debugpro-bug-hunt`: finds evidence-backed bugs from diffs, logs, stack traces, Sentry events, and bounded static inspection.
- `debugpro-source-runtime-parity`: proves whether source, packaged, installed, cached, and live runtime files match.
- `debugpro-browser-runtime-proof`: captures browser, localhost, UI, console, network, and runtime proof.
- `debugpro-frontend-debugging`: connects frontend rendering, routing, hydration, assets, and state failures to evidence.
- `debugpro-ci-pr-failure`: diagnoses CI, GitHub Actions, PR check, and workflow failures.
- `debugpro-mcp-runtime-ownership`: finds which MCP config, server, connector, cache, or runtime owns a tool failure.
- `debugpro-macos-debugging`: debugs macOS app build, signing, launch, process, log, and desktop runtime issues.
- `debugpro-performance`: diagnoses latency, throughput, CPU, memory, query, and browser performance issues.
- `debugpro-root-cause-tracing`: traces a symptom through layers until the causal chain is proven or bounded.
- `debugpro-instrumentation`: selects or adds bounded temporary evidence probes.
- `debugpro-verify`: verifies fixes against the original failing signal.
- `debugpro-bisect`: finds regression windows.
- `debugpro-delta`: builds minimal reproductions and reduces failing inputs.
- `debugpro-flaky`: isolates flaky, order-dependent, timing-sensitive, or seed-sensitive tests.
- `debugpro-team`: coordinates safe multi-track debugging before arbitration.

## Agents

- `debugpro-capability-router`: returns a compact routing packet with the primary route, evidence, references, tools, fallbacks, parallel escalation, and stop conditions.
- `debugpro-investigator`: investigates exactly one hypothesis with read-only evidence and a structured verdict.

## Optional Evidence Tools

DebugPro can name optional tools such as Tool Finder, Browser, Chrome, Chrome DevTools MCP, Playwright, VS Code MCP, GitHub MCP, `gh`, `actionlint`, `act`, MCP Inspector, MCPJam, `mcp-debug`, `mcp-status`, Context7 MCP, Context7 CLI fallback, Render, Vercel, Cloudflare, Supabase, Sentry, Grafana, Datadog, Loki, OpenTelemetry-style logs/metrics/traces, and shell commands. These are not bundled dependencies. If a capability is unavailable, DebugPro should state that and use the closest local fallback.

Tool Finder is scoped to DebugPro maintenance and capability discovery. Do not
use it as the default first probe for ordinary debugging; route by the failing
symptom first, then use Tool Finder only if the user explicitly asks which
tools, plugins, agents, skills, MCPs, or connectors should be added or compared.

## Source And Runtime Policy

Edit the checked-out source plugin, not an active runtime cache directory. Source changes, validation, and evidence collection come first; installation is a publication step after source validation passes.

`.codex-plugin/plugin.json` is the only canonical manifest.

## Cache Sync

The sync script is dry-run by default:

```bash
DEBUGPRO_ROOT="${CODEX_PLUGIN_ROOT:-$PWD}"
python3 "$DEBUGPRO_ROOT/scripts/sync_debugpro_cache.py"
```

After validation passes, sync the active local cache:

```bash
python3 "$DEBUGPRO_ROOT/scripts/sync_debugpro_cache.py" --apply
```

## Local Validation

```bash
DEBUGPRO_ROOT="${CODEX_PLUGIN_ROOT:-$PWD}"
mkdir -p "$DEBUGPRO_ROOT/.tmp"
python3 "$DEBUGPRO_ROOT/scripts/validate_debugpro.py" --root "$DEBUGPRO_ROOT"
python3 "$DEBUGPRO_ROOT/scripts/collect_debug_context.py" "$DEBUGPRO_ROOT" >/tmp/debugpro-context.json
python3 "$DEBUGPRO_ROOT/scripts/check_debugpro_duplication.py" --root "$DEBUGPRO_ROOT"
python3 -m json.tool "$DEBUGPRO_ROOT/.codex-plugin/plugin.json" >/dev/null
python3 -m compileall "$DEBUGPRO_ROOT/scripts"
python3 -m unittest discover "$DEBUGPRO_ROOT/tests"
python3 "$DEBUGPRO_ROOT/scripts/validate_shared_evidence.py" "$DEBUGPRO_ROOT/skills/debugpro/references/shared-evidence.v1.example.json"
bash -n "$DEBUGPRO_ROOT/skills/debugpro-flaky/scripts/find-polluter.sh"
(cd "$DEBUGPRO_ROOT" && plugin-eval benchmark . --config .plugin-eval/benchmark.json)
python3 "$DEBUGPRO_ROOT/scripts/sync_debugpro_cache.py"
```

Use the validation script before publishing and after any routing, manifest, reference, skill, or agent change.

## Ownership Boundaries

DebugPro owns active evidence-first debugging: symptoms, hypotheses, runtime proof, source/cache parity, CI failure diagnosis, MCP ownership, and verification against the original failing signal. Use Plan Architect for implementation plans and handoffs, comprehensive-review or CodeRabbit-style review for broad code review, agent-teams for independently scoped execution tracks, and specialized browser/Chrome tools only as evidence collectors inside the owning DebugPro route. Universal or generic debugger plugins should not override DebugPro routing unless the user explicitly asks for that tool.
