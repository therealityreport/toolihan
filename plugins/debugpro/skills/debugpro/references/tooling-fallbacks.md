# DebugPro Tooling Fallbacks

Use this when `capability-router.md` selects an optional capability that is
unavailable, unauthenticated, stale, or unsafe to use.

## Fallback Ladder

| Preferred signal | Fallbacks |
| --- | --- |
| Browser automation | `curl`, app logs, static screenshots, saved HTML, server responses. |
| Chrome profile/session | in-app browser, fresh local profile, HTTP probes, visible app state supplied by user. |
| Chrome DevTools MCP | browser console export, Playwright trace, app logs, network HAR if available. |
| Playwright MCP | local Playwright CLI, screenshot-only proof, manual reproduction notes. |
| GitHub MCP | `gh`, workflow log artifacts, repository files, local `actionlint`, `act` where safe. |
| Cloud/deploy connector | provider CLI, dashboard-exported logs, deployment manifests, environment diffs. |
| Observability platform | raw logs, trace IDs from app logs, metrics snapshots, deploy timestamps. |
| MCP inspector tools | `mcp-status`, config files, process list, server logs, stdio handshake logs. |
| Profiler | coarse timing, resource counters, logs around hot path, repeatable benchmark. |
| Production data | sanitized sample, staging reproduction, schema/config inspection, read-only query. |

## Rules

- Prefer read-only evidence before mutating runtime state.
- Name the missing tool and the fallback selected.
- Do not block on a premium or unauthenticated tool if local evidence can answer the same question.
- If all available fallbacks are weak, label the conclusion as bounded rather than proven.
