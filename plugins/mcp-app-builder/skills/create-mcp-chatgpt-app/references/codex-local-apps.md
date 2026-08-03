# Codex Local Apps

Use this reference for local-only Codex app/plugin validation and planning.

## Config Ownership

- User-level config lives at `~/.codex/config.toml`.
- Local checks may inspect `plugins.*`, `apps.*`, and `mcp_servers.*` entries.
- Project-local config is not the owner for every machine-local app or plugin visibility decision.
- Do not print config contents or secret values while checking local state.

## Local-Only Scope

Local-only apps usually skip these unless the user asks for them:

- public submission
- screenshots
- privacy/support metadata
- auth
- storage
- deployment
- HTTPS tunnel setup

HTTPS tunnels are useful for ChatGPT web testing, but they are not required for every local Codex validation pass.

## Connecting Local Apps To Codex (verified against codex-cli 0.142.x)

- Register a local Streamable HTTP MCP server with `codex mcp add <name> --url http://localhost:<port>/mcp`. This writes a clean `[mcp_servers.<name>]` entry (the CLI owns TOML merging, so existing servers are untouched). `codex mcp remove <name>` reverses it. `[mcp] remote_mcp_client_enabled = true` must be set (it is, by default).
- The orchestrator `connect_codex_app.mjs` automates start → `/healthz` → verify → `codex mcp add`, backing up `config.toml` first and only registering after verification passes.
- Widget rendering does NOT require a connector/app. Codex reads a tool's `text/html;profile=mcp-app` resource directly from the named MCP server (app-server `McpResourceRead(server, uri)` + `McpServerToolCall`). A tool with `_meta.ui.resourceUri` + `openai/outputTemplate` plus a registered resource renders inline once the server is connected.
- Current packaged plugin apps use backend-issued `plugin_asdk_app_...` ids; legacy plugins may still contain `asdk_app_...`. There is no `codex` CLI subcommand that mints these ids. Create/test the app in ChatGPT developer mode, copy the real id, then put it in the plugin's `.app.json`. Do not fabricate ids; `check_mcp_app_state.mjs` rejects synthetic `link_id`s.

## Codex Plugin Package

- A ready-to-install local plugin needs `.codex-plugin/plugin.json` with `mcpServers: "./.mcp.json"`.
- The generated `.mcp.json` launches `mcp/server.bundle.mjs --stdio` through `${CLAUDE_PLUGIN_ROOT}` so the cached install remains portable.
- When a real app id is available, the plugin manifest also points `apps` at `./.app.json`.
- A local marketplace entry makes the plugin installable through the Codex plugin directory; it is packaging metadata, not a substitute for a real app id.

## Source And Cache

- Source plugin edits belong in the source plugin directory first.
- Cache copies are runtime artifacts and should not be edited as the primary source.
- Source/cache parity is mandatory after plugin edits when the cache is part of the active runtime.
- Drift should be reported as status unless the user explicitly asks for sync or mutation.

## Installed-App Fleet Checks

Use `check_mcp_app_state.mjs --all-installed` when the question spans more than one plugin. It compares enabled/disabled config rows, cached `.app.json` ownership, action-cache wrappers, and optional source manifests. A plugin with a shared hosted connector may have `.app.json` without `.mcp.json`; classify it as `shared_connector` when the App ID and live action ownership are present instead of adding a fake local server. Apply mode only removes wrappers for Apps explicitly disabled in config, creates timestamped backups, and leaves orphan config rows and links for approval.
