# MCP App Surfaces

Use this reference when wrapping existing MCP servers as local apps or validating app metadata.

## Surface Rules

- Each connected MCP should surface under its own app name.
- App actions should expose real MCP capabilities, not only a renderer command such as `render_pdfx_app`.
- Tool titles and descriptions should describe actual operations.
- Widget resources support the app. They are not the app's whole ability.
- Avoid aggregate wrapper rows when the real MCP can be represented under its own identity.

## Metadata Locations

- `.app.json` app IDs live under `apps.<key>.id`; current plugin app IDs start with `plugin_asdk_app_`, while legacy `asdk_app_` IDs remain valid.
- `.mcp.json` MCP entries live under `mcpServers.<key>`.
- MCP entries may be command-based or URL-based.
- Bridge or tunnel runtime metadata can live separately, such as `apps/personal-mcp-apps/runtime/tunnels.json`.

## URL Stability

- `local`: localhost, 127.0.0.1, or private-network URLs.
- `ephemeral`: temporary tunnel hosts such as `trycloudflare.com`, `loca.lt`, `ngrok-free.app`, or `ngrok.io`.
- `stable`: non-local HTTPS URLs that are not known temporary tunnel hosts.
- `missing`: no URL is present.

Quick tunnels are fine for smoke tests. Durable app IDs should use stable URLs.
