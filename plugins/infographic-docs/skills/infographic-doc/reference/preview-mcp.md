# Playwright MCP preview

`infographic-docs` ships a Codex MCP config at the plugin root:

```json
{
  "mcpServers": {
    "infographic-preview-playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

The actual `.mcp.json` adds headless Chrome, vision/PDF capabilities, localhost-only origins, and a knowledge-base output folder.

## Preview flow

1. Generate the doc under `${KB_ROOT}/info-docs/<topic-slug>/`.
2. Start a local static server from that doc folder.
3. Open `http://localhost:<port>/index.html` through the `infographic-preview-playwright` MCP server.
4. Capture screenshots, snapshots, PDF output, and console warnings as needed.

Prefer localhost previews over `file://` previews. The MCP config intentionally avoids unrestricted file access.

## Local server command

From the generated doc folder:

```bash
python3 -m http.server 8765
```

Then open:

```text
http://localhost:8765/index.html
```

## What to check

- The first viewport shows the document identity clearly.
- The tab bar links navigate to real HTML files.
- The active tab state changes per page.
- Mermaid or rendered chart assets are visible if the doc uses them.
- The layout works at desktop and mobile widths.
- Console warnings are explained or fixed.

Do not require Playwright MCP for every generated doc. Use it when the user asks for preview proof, when visual assets were rendered, or when layout risk is high.
