# Decodo Plugin

Decodo gives Codex a focused scraping and proxy workflow layer: MCP setup, SDK/API helpers, scraper
skills, proxy operations, troubleshooting, and workflow specs.

## Active Surfaces

- `skills/` tells Codex how to choose Decodo MCP, SDK/API, browser/Scrapy, proxy, rank tracking,
  Reddit/news/visual, and troubleshooting workflows.
- `.mcp.json` is retained as on-demand launcher metadata for explicit Decodo scraping/setup/debug work.
  It is not advertised from `.codex-plugin/plugin.json`, so Codex does not start `@decodo/mcp-server`
  during unrelated chats.
- The MCP command uses `npx` from `PATH` and pins the server package version.
- `scripts/` contains safe doctor and smoke-check commands.
- `tools/` contains helper modules used by scripts. These are not direct Codex tools by themselves.
- `agents/` contains agent-style specs that are routed through `skills/decodo-agent-workflows/`.

## Setup

Do not put secret values in plugin files. Store them in macOS `launchctl` so ChatGPT/Codex can
inherit them when it starts.

### MCP Token

```bash
cd plugins/decodo
node scripts/setup-decodo-mcp-token.mjs
node scripts/doctor-decodo-connection.mjs --dry-run
```

Then fully quit and reopen ChatGPT/Codex only if you intentionally connect the Decodo MCP server
for a Decodo scraping task.

### Post-Setup Live Smoke

This starts the MCP process briefly and sends no tool calls:

```bash
cd plugins/decodo
node scripts/smoke-decodo-mcp-after-setup.mjs --live
```

### Proxy Credentials

Only set this if you need proxy rotation checks:

```bash
cd plugins/decodo
node scripts/setup-decodo-proxy-launchctl.mjs
node scripts/setup-decodo-proxy-launchctl.mjs --status
node scripts/doctor-decodo-proxies.mjs --dry-run
```

### Cache Reset

If the plugin view still shows stale rows after a restart:

```bash
cd plugins/decodo
node scripts/reset-decodo-plugin-cache.mjs --apply
```

## Smoke Checks

Dry runs never touch Decodo:

```bash
node scripts/doctor-decodo-auth.mjs --dry-run
node scripts/doctor-decodo-connection.mjs --dry-run
node scripts/smoke-decodo-mcp.mjs --dry-run
node scripts/smoke-decodo-sdk.mjs --dry-run
node scripts/smoke-proxy-rotation.mjs --dry-run
```

Live checks require credentials and fail closed when credentials are missing:

```bash
node scripts/doctor-decodo-auth.mjs --live
node scripts/doctor-decodo-connection.mjs --live
node scripts/smoke-decodo-mcp.mjs --live
node scripts/smoke-decodo-sdk.mjs --live --package @decodo/sdk-ts
node scripts/smoke-proxy-rotation.mjs --live
```

## Troubleshooting

- If ChatGPT shows `connector_decodo`, it is showing stale cache. Run
  `node scripts/reset-decodo-plugin-cache.mjs --apply`, then fully quit and reopen ChatGPT/Codex.
- If stale rows remain after restart, uninstall and reinstall the Decodo plugin from the local marketplace.
- If the MCP server will not connect, run `node scripts/doctor-decodo-connection.mjs --dry-run`.
- If shell env is present but launchctl env is missing, run `node scripts/setup-decodo-mcp-token.mjs`.
- If launchctl env is present but shell env is missing, restart ChatGPT/Codex so the app inherits it.
- If live smoke checks still say credentials are missing, the app process did not inherit the token.
- If MCP launch fails with `spawn npx ENOENT`, confirm `npx` is available on the app `PATH`.
- If you need to clear the token, run `node scripts/setup-decodo-mcp-token.mjs --clear`.
- If you need to clear proxy credentials, run `node scripts/setup-decodo-proxy-launchctl.mjs --clear`.

## Safety

- Keep concurrency low by default.
- Prefer MCP/API managed scraping before raw proxy escalation.
- Do not scrape private, auth-gated, paywalled, or sensitive personal data without rights and a
  lawful basis.
- Do not use this plugin for credential abuse, purchase automation, spam, harassment, malware,
  denial-of-service behavior, or unauthorized access.
- Scripts redact tokens, credentials, proxy URLs, and authorization headers before printing output.

## Marketplace

The shared Codex marketplace entry is managed by
`superpowers-marketplace/scripts/local-plugins-scope.json` and projected into the single
user-level `local-plugins` marketplace. Decodo should live as the `plugins/decodo`
plugin folder.
