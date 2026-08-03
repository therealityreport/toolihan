---
name: create-mcp-chatgpt-app
description: Plan, scaffold, package, and validate MCP Apps, Codex plugin Apps, or ChatGPT Apps using current Apps SDK and Codex plugin guidance.
---

# Create MCP ChatGPT App

Use this skill when the user wants to create, plan, scaffold, harden, or validate an MCP App, ChatGPT App, or Apps SDK project.

## Source Order

1. Prefer current official docs from the OpenAI Developers plugin for Apps SDK questions.
2. Use MCP Apps docs for bridge behavior, resource metadata, and MCP App extension terms.
3. Prefer official upstream examples when a requested app matches an existing example closely.
4. Use the local scaffold script only for the three short-path archetypes below.

## Routing

| Route | Use When |
| --- | --- |
| `codex-local` | Plan or validate a local-only Codex app/plugin surface; use `references/codex-local-apps.md` and keep checks read-only unless mutation is requested. |
| `wrap-existing-mcp` | Wrap a real existing MCP server under its own local app/plugin identity; use `references/mcp-app-surfaces.md` and preserve real action tools. |
| `docs-refresh` | Refresh OpenAI Developers docs first, then Context7 when needed, before changing generated behavior or SDK-specific guidance. |
| `tool-inventory` | Use Tool Finder before deciding what local tool, MCP, or plugin should be wrapped. |
| `codex-plugin` | Generate a distributable Codex plugin whose bundled MCP server and optional backend-issued app reference are installed together. |

## Archetypes

| Archetype | Behavior |
| --- | --- |
| `tool-only` | Generate a Node MCP server with one typed tool, annotations, `outputSchema`, Streamable HTTP transport, and no widget. |
| `vanilla-widget` | Generate a Node MCP server plus `public/widget.html`, `registerAppResource`, `registerAppTool`, `RESOURCE_MIME_TYPE`, widget CSP metadata, and MCP Apps bridge calls. |
| `interactive-decoupled` | Generate the vanilla widget plus a separate data tool that the widget calls through `tools/call`; use this when render and data refresh should be separated. |
| `react-widget` | Do not generate locally. Adapt the closest official React or bundled UI example, then run the same validation checks and add project-specific state handling. |
| `submission-ready` | Do not generate locally. Start from an existing scaffold or upstream example, then add auth, privacy/security review, metadata optimization, test cases, and submission checklist artifacts. |

## Scaffold Command

From the plugin root:

```bash
node scripts/scaffold_node_app.mjs --name "Smoke App" --out /tmp/smoke-app --archetype vanilla-widget
```

Expected pass signal:

```text
Created Smoke App at /tmp/smoke-app
```

Supported local archetypes are `tool-only`, `vanilla-widget`, and `interactive-decoupled`.

## Ready-to-use Codex Plugin App

Use the `codex-plugin` target when the deliverable should be an installable plugin instead of a standalone MCP project:

```bash
node scripts/scaffold_node_app.mjs \
  --name "My Plugin App" \
  --out /path/to/marketplace/plugins/my-plugin-app \
  --archetype vanilla-widget \
  --target codex-plugin \
  --marketplace /path/to/marketplace/.agents/plugins/marketplace.json

cd /path/to/marketplace/plugins/my-plugin-app
npm install
npm run check
node /path/to/mcp-app-builder/scripts/validate_app_scaffold.mjs .
```

The generated plugin includes `.codex-plugin/plugin.json`, `.mcp.json`, the app source/widget, and a self-contained `mcp/server.bundle.mjs` built during `npm install`. The plugin launcher uses stdio, while `npm start` keeps the HTTP `/mcp` development loop available.

When ChatGPT developer mode has issued a current plugin app id, add `--app-id plugin_asdk_app_...`. That also creates `.app.json` and wires the manifest `apps` field. Legacy `asdk_app_...` ids remain accepted for existing plugins. Never invent either form.

## Generated Project Checks

For standalone targets, run this before handing off:

```bash
node scripts/validate_app_scaffold.mjs /tmp/smoke-app
```

Expected pass signal:

```text
Scaffold validation passed
```

Then run the generated project's dependency and TypeScript check when network and package installation are available:

```bash
cd /tmp/smoke-app
npm install
npm run check
```

Expected pass signal: both commands exit `0`; `npm run check` emits no TypeScript errors.

For `codex-plugin` targets, run `npm install` first because it builds the required `mcp/server.bundle.mjs`, then run `npm run check` and the scaffold validator. Missing bundle, plugin manifest, MCP launcher, or invalid app id is a validation failure.

## App Action Contract

Every generated tool must declare action annotations. `readOnlyHint` is the explicit read/write intent that Codex and ChatGPT use to label App actions, and `destructiveHint`, `openWorldHint`, and `idempotentHint` describe whether the action mutates data, reaches outside the local app, or can be safely repeated. Do not omit these hints, even for simple read-only render tools.

Every generated widget action must also expose Apps SDK metadata on the tool config: `ui.resourceUri`, `openai/outputTemplate`, `openai/toolInvocation/invoking`, and `openai/toolInvocation/invoked`. The widget resource must publish `text/html;profile=mcp-app` content with `_meta.ui` CSP/border/permission metadata and `openai/widgetDescription`. These fields drive the App action UI and host rendering path; missing fields are validation failures, not warnings.

## Connect to Codex (fully automated)

Use `connect_codex_app.mjs` to close the loop from a scaffold to a running, registered, verified app in Codex (Codex CLI + Codex.app). It scaffolds (optional), installs, starts the server on a free port, waits for `/healthz`, verifies the MCP connection, and only then registers the server with `codex mcp add`. It is fully automated (no prompts) but non-destructive: `~/.codex/config.toml` is backed up before any mutation, registration is fail-closed on verification, and teardown only stops processes this tool started.

```bash
# Scaffold + connect in one command (widget app), then use it in Codex:
node scripts/connect_codex_app.mjs up --app /tmp/my-app --name "My App" --archetype vanilla-widget --mode mcp-server

# Inspect / tear down:
node scripts/connect_codex_app.mjs status --app /tmp/my-app
node scripts/connect_codex_app.mjs down --app /tmp/my-app        # add --purge to remove .mcp-app/
```

Modes:

| Mode | Result |
| --- | --- |
| `mcp-server` (default) | Registers a Streamable HTTP MCP server. Tools **and widgets** are usable in Codex CLI and Codex.app — Codex reads the `text/html;profile=mcp-app` resource directly from the named server (`McpResourceRead`), so no account/connector step is needed. |
| `apps-app` | Legacy standalone workflow that writes URL-based `.mcp.json` metadata and prints publishing guidance. Do not use it for the `codex-plugin` target because that target owns a bundled stdio launcher. |

App-id constraint: current Codex plugin apps use backend-issued `plugin_asdk_app_...` ids; older installed apps may still use `asdk_app_...`. There is no `codex` command that mints either id locally. Test the MCP app in ChatGPT developer mode, copy the real id from the created app, then scaffold/package the plugin with `--app-id`. Never fabricate an app id.

After `up`, Codex CLI picks up the server on its next session; Codex.app needs a reload/restart to see it. For manual/standalone runtime checks, run the probe against the running server:

```bash
node scripts/verify_codex_connection.mjs --app /tmp/my-app --port <port> --call
```

Only set up an HTTPS tunnel when the user asks for ChatGPT web testing.

## Plugin Validation

When editing this plugin, run the available local checks:

```bash
python3 $HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ${CLAUDE_PLUGIN_ROOT}
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_node_app.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/validate_app_scaffold.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/check_codex_local_app.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/recreate_mcp_apps_from_urls.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/sync_codex_local_app_directory.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/connect_codex_app.mjs
node --check ${CLAUDE_PLUGIN_ROOT}/scripts/verify_codex_connection.mjs
```

Expected pass signals:

```text
Plugin validation passed: ${CLAUDE_PLUGIN_ROOT}
```

`node --check` exits `0` and prints no syntax errors.

Use the read-only local checker for source/config/cache status:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_codex_local_app.mjs --plugin ${CLAUDE_PLUGIN_ROOT} --id mcp-app-builder --json
```

Use the read-only MCP app state checker for app IDs, MCP entries, tunnel stability, and action-surface status:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs --plugin /path/to/plugin --bridges /path/to/tunnels.json --json
```

When a Codex local app should expose callable actions, require real generated action links instead of app-directory-only rows:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs --plugin /path/to/plugin --bridges /path/to/tunnels.json --require-codex-action-cache
```

Expected pass signal: every `apps.<key>` with a `plugin_asdk_app_...` (or legacy `asdk_app_...`) id has a corresponding Codex action cache entry with at least one real `link_...` id. A missing action cache means the app is listed but not actually callable. A synthetic link generated from the app id is invalid; recreate or reconnect the app through the real app flow instead of fabricating `codex_apps_tools` records.

For an installed-plugin fleet, use the same checker across config, plugin cache, source, and action cache:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs --all-installed --source-root /path/to/plugins --json
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs --all-installed --source-root /path/to/plugins --dry-run --json
```

This reports bundled MCP Apps, hosted Apps, shared connector wrappers, disabled-but-cached actions, unloaded/auth/connection states, orphan config rows, and source/cache drift. `--apply` removes only disabled cached action wrappers after writing sibling backups; it never deletes config rows or App links. Restore one backup with `--rollback /path/to/file.bak-mcp-app-state-...`.

When a local plugin's `.app.json` declarations appear in `app/list` as raw app-id placeholders, sync app discovery metadata into Codex's local app-directory cache:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync_codex_local_app_directory.mjs --plugin /path/to/plugin --write
```

This only repairs local app names, descriptions, icons, and plugin ownership in app discovery. It must not be used as a substitute for real action/tool link cache entries.

Use watch mode when waiting for local metadata or tunnel files to settle:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/check_mcp_app_state.mjs --plugin /path/to/plugin --bridges /path/to/tunnels.json --watch --interval 5
```

Use the dependency-free recreation helper when MCP apps must be manually recreated from `.mcp.json` URLs or tunnel metadata. The default mode prints a checklist and does not call ChatGPT APIs or a browser:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/recreate_mcp_apps_from_urls.mjs --plugin /path/to/plugin --bridges /path/to/tunnels.json
```

After manually creating apps and saving real `plugin_asdk_app_...` IDs in `created-apps.json`, update root `.app.json` with:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/recreate_mcp_apps_from_urls.mjs --plugin /path/to/plugin --bridges /path/to/tunnels.json --created-apps /path/to/created-apps.json --write
```

The helper refuses missing or invalid app IDs and warns when selected URLs are ephemeral tunnel URLs such as `trycloudflare.com`.
When `.mcp.json` provides a stable HTTPS URL and bridge metadata also contains an ephemeral tunnel URL, the helper selects the stable `.mcp.json` URL. This matches the Apps SDK quickstart and examples: the host must create/connect the app against a reachable `/mcp` endpoint so it can generate real action links.

## Implementation Rules

- Keep generated starters small and inspectable.
- Include `annotations` and `outputSchema` on generated tools. Treat `readOnlyHint` as the App action read/write UI signal and always set `destructiveHint`, `openWorldHint`, and `idempotentHint` explicitly.
- Use `structuredContent`, `content`, and `_meta` deliberately.
- For widgets, include `ui.resourceUri`, `openai/outputTemplate`, `openai/toolInvocation/invoking`, `openai/toolInvocation/invoked`, and widget resource `_meta.ui` metadata.
- For widgets, prefer MCP Apps bridge messages such as `ui/initialize`, `ui/notifications/initialized`, `ui/notifications/tool-result`, and `tools/call`.
- Treat `window.openai` as optional host context, not the primary transport.
- Do not place secrets, API keys, tokens, or placeholder secret names in generated files.
- Do not add React, bundlers, databases, auth, monetization, or deployment files unless the user asks for that stage.
- If marketplace or install state is changed, make a timestamped `marketplace.json` backup first; rollback is restoring that backup and removing the plugin directory/cache created during the failed mutation.
