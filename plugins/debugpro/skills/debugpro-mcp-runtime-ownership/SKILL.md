---
name: debugpro-mcp-runtime-ownership
description: Use when MCP tools, servers, configs, caches, or owners drift.
---

# DebugPro MCP Runtime Ownership

Use this route to prove which MCP config, server, connector, cache, or runtime
owns a tool failure.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/mcp-runtime-ownership.md`
- `../debugpro/references/secret-redaction.md`

## When To Use

- An MCP tool is missing, duplicated, stale, failing to start, or exposed by the wrong runtime.
- User, project, app, plugin, and cache MCP config may overlap.
- A manifest or install check passes, but the active session cannot call the expected tool.

## Required Evidence

- Exact tool/server name, requested action, error text, session context, and expected owner.
- Config paths, manifest entries, cache version, active tool list, process state, and logs.
- Server command, args, env, cwd, transport, auth state, and any attempted refresh.

## First Probes

1. Run `python3 scripts/collect_mcp_owner_context.py` from the plugin root when local ownership evidence is needed. It reports config keys, not values, and redacts command output.
2. Use the MCP Inspector when it is available; confirm initialize, protocol version, and declared capabilities.
3. Identify transport: stdio logs are host-captured stderr; Streamable HTTP needs HTTP/log-notification evidence.
4. Compare configured, installed, launched, negotiated, exposed, and callable state.
5. Confirm absolute `command` paths, absolute data/env paths, and explicit required `env` values.
6. Check duplicate names, stale cache entries, broken commands, cwd-sensitive paths, and permission failures.
7. Verify a fix by proving the active session exposes and can call the expected tool.

## Stop Conditions

- The next step would edit global config, disable unrelated tools, rotate secrets, or require credentials.
- Ownership remains ambiguous across concurrent edits or multiple runtimes.
- Required logs, config files, tool inventory, or runtime diagnostics are unavailable.
- Captured evidence contains secrets that have not been redacted.

## Output Format

```markdown
## MCP Runtime Ownership Report
- Tool/server symptom:
- Expected owner:
- Active owner:
- Config paths checked:
- Runtime/cache evidence:
- Health/log evidence:
- Cause:
- Fix or refresh needed:
- Active-session verification:
- Stop condition or residual risk:
```
