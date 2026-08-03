# @ChromeDevTools

`@ChromeDevTools` is a local-first Chrome DevTools plugin for collecting browser evidence, API call summaries, redacted reproduction commands, and repair guidance from Chrome DevTools style data.

The plugin keeps fixture and dry-run flows for safe reproduction, and uses the official Chrome DevTools MCP as the gated live DevTools backend. Isolated upstream sessions are the default. Profile-connected modes such as `autoConnect`, `browserUrl`, and `wsEndpoint` require a route token, friendly profile label, and URL allow/block policy before delegated tools run.

## First-slice workflow

1. Confirm local readiness:

```bash
node bin/cdt doctor
node bin/cdt doctor context7
node bin/cdt doctor upstream-mcp
```

2. Preview what would be collected from the active target without attaching live:

```bash
node bin/cdt collect --target active --console --network --dom --screenshot --dry-run
```

3. Inspect API calls from fixture data and include safe cURL output:

```bash
node bin/cdt api calls --target active --include-curl --dry-run
node bin/cdt api curl --run test/fixtures/debug-run/basic --api-call api-call-1
```

4. Compare or replay fixture debug runs:

```bash
node bin/cdt compare test/fixtures/debug-run/failing test/fixtures/debug-run/fixed --api --console --screenshot
node bin/cdt replay test/fixtures/debug-run/basic --format summary
```

5. Redact fixture content and list MCP metadata:

```bash
node bin/cdt redact test/fixtures/redaction/sensitive
node bin/cdt mcp serve --stdio --caps core,evidence,network,debugging,performance,memory,experimental --list-tools
```

6. Create a route-session plan before live evidence:

```bash
node bin/cdt route create --connection-mode isolated --dry-run
node bin/cdt route create --connection-mode autoConnect --allowed-url-pattern 'https://example.com/*' --route-label debug-session
node bin/cdt route list
node bin/cdt route inspect --route-token rt_example
node bin/cdt route revoke --route-token rt_example
```

7. Collect redaction-first live evidence through a route token:

```bash
node bin/cdt live collect --route-token rt_example --network --console --snapshot --screenshot --output ./.chrome-devtools-runs/run-001 --dry-run
node bin/cdt replay ./.chrome-devtools-runs/run-001
node bin/cdt compare ./.chrome-devtools-runs/before ./.chrome-devtools-runs/after
```

8. Run Lighthouse or performance traces through gated upstream MCP:

```bash
node bin/cdt lighthouse audit --route-token rt_example --output ./lighthouse-summary.json
node bin/cdt perf trace start --route-token rt_example --label before
node bin/cdt perf trace stop --route-token rt_example --output ./trace-summary.json
node bin/cdt perf insight --run ./trace-summary.json --insight LCP
```

9. Investigate browser memory through bounded local aliases:

```bash
node bin/cdt memory capture --route-token rt_example --file .chrome-devtools-runs/memory/baseline.heapsnapshot
node bin/cdt memory compare --route-token rt_example --base .chrome-devtools-runs/memory/baseline.heapsnapshot --current .chrome-devtools-runs/memory/final.heapsnapshot
node bin/cdt memory details --route-token rt_example --file .chrome-devtools-runs/memory/final.heapsnapshot --filter objectsRetainedByDetachedDomNodes --page-size 50
```

9. Sync local install/cache copies after a validated change:

```bash
npm run sync:install:dry-run
npm run sync:install
npm run sync:install:verify
npm run sync:startup-check
npm run sync:inventory-smoke
npm run sync:status
npm run sync:plugin-health
npm run sync:repair
npm run sync:repair-prompts
npm run sync:repair-runtime-cache
```

## What this slice supports

- API Discovery Workbench summaries from fixture or dry-run data.
- Redacted cURL generation for reproducing API calls safely.
- Route-session planning for isolated and profile-connected upstream MCP modes.
- Upstream Chrome DevTools MCP compatibility checks and gated live delegation.
- Delegated live evidence aliases for network requests, console messages, snapshots, screenshots, Lighthouse, and performance traces.
- Bounded heap snapshot capture, comparison, filtered aggregates, class nodes, retainers, retaining paths, dominators, edges, and duplicate-string counts through locally constrained aliases.
- Install/cache sync for local Codex plugin copies.
- Codex startup drift checks, Plugins UI stuck-state detection, global prompt-limit repair, runtime-cache drift repair, shared marketplace scope sync, inventory smoke checks, compact status output, and rollback support.
- Response metadata summaries, with body capture blocked unless bounded and redacted.
- Safe target previews that avoid exposing unrelated tab details.
- Evidence timelines and debug-run diffs for comparing failing and fixed runs.
- Error fingerprints that group similar console, network, and runtime failures.
- Bridge doctor checks for CLI, schema, Context7, adapter boundaries, and fixture readiness.
- Page-exposed WebMCP and third-party developer tools as list-only untrusted metadata. Execution is disabled by default.

## Live delegation

Live `@Chrome` tab control remains owned by the `@chrome` plugin. `@ChromeDevTools` uses upstream Chrome DevTools MCP for live DevTools evidence after route-token, connection-source, and redaction gates pass.

Default upstream invocation:

```bash
npx -y chrome-devtools-mcp@1.6.0 --isolated --experimentalPageIdRouting --redactNetworkHeaders --no-usage-statistics --no-performance-crux
```

Profile-connected modes are allowed, but must carry an explicit route token:

```bash
node bin/cdt doctor upstream-mcp --connection-mode autoConnect --route-token rt_example --allowed-url-pattern 'https://example.com/*'
```

URL allow/block policy is recommended for profile-connected routes and can be required by running the doctor with `--strict`. Visible output should use friendly Chrome profile names such as `Codex`, `Work`, `Personal`, or `openai-agent`.

Delegated upstream tools are visible through MCP metadata, but remain gated:

- `list_network_requests`
- `get_network_request`
- `list_console_messages`
- `take_snapshot`
- `take_screenshot`
- `lighthouse_audit`
- `performance_start_trace`
- `performance_stop_trace`
- `performance_analyze_insight`
- `take_heapsnapshot`
- `get_heapsnapshot_summary`, `get_heapsnapshot_details`, `get_heapsnapshot_class_nodes`
- `compare_heapsnapshots`
- `get_heapsnapshot_retainers`, `get_heapsnapshot_retaining_paths`, `get_heapsnapshot_edges`, `get_heapsnapshot_dominators`, `close_heapsnapshot`
- `get_heapsnapshot_duplicate_strings` (values are redacted and hashed)

Page-exposed tools are discovery-only:

- `webmcp_tools_list`
- `third_party_tools_list`

## Safety defaults

- Do not emit cookies, bearer tokens, API keys, CSRF tokens, session headers, or secret query parameters.
- Keep response body capture metadata-only by default.
- Block unresolved or unredacted response bodies from summaries and reports.
- Limit target preview fields to safe title, origin/path, profile label, recency, and match reason.
- Keep generated commands reproducible without requiring active browser credentials.
- Keep isolated routes as the default.
- Require route-token ownership for profile-connected routes.
- Keep usage statistics and performance CrUX disabled by default.
- Keep raw `--memoryDebugging` out of global/runtime configuration. It is enabled only in the local memory-alias child process, with relative snapshot paths and bounded output.
- Redact evidence before summaries, replay, compare, cURL, or API inventory output.
