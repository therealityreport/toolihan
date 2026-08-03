# External tool routing

The default output is still standalone multi-page HTML with the bundled stylesheet. External tools are opt-in helpers. Use them only when they make the doc materially better or when the user asks for them.

## Routing table

| Need | Tool | How to use it | Adoption |
|---|---|---|---|
| The user explicitly says "use shadcn" or asks for an app-style doc surface | `shadcn` | Use `npx shadcn@latest add <components> --dry-run` first, then build in the target app or a clearly named app-mode folder. | Optional mode |
| Preview generated HTML with browser tooling | `infographic-preview-playwright` MCP | Serve the doc folder over localhost, then use the Playwright MCP tools to navigate, snapshot, screenshot, or export PDF. | Optional MCP |
| Add simple flowcharts, timelines, sequences, or state diagrams | `mermaid` or `@mermaid-js/mermaid-cli` | Use inline `<pre class="mermaid">` for browser-rendered diagrams, or `scripts/render-visuals.mjs` for generated assets. | Partial integration |
| Add charts from small structured data | `vega-lite` and `vega` | Store `.vl.json` specs under `visuals/` or `assets/visuals/`, then run `scripts/render-visuals.mjs`. | Partial integration |
| Add custom data visuals where specs are too limiting | `@observablehq/plot` or `d3` | Borrow chart patterns. Do not make these runtime dependencies unless the doc needs live rendering. | Reference |
| Check generated HTML structure | `html-validate` | Optional validation command outside the doc content. | Optional validation |
| Check links and images | `linkinator` | Optional validation command against localhost or the doc folder. | Optional validation |
| Check accessibility | `pa11y`, `axe-core`, or `lighthouse` | Optional validation command against localhost. | Optional validation |

## Linking rules

- Prefer a local script or reference doc over copying whole third-party repos into this plugin.
- Prefer `npx -y <package>@latest` for optional CLIs so the plugin does not require global installs.
- Add MCP wiring only for real MCP servers. Packages like `html-validate`, `linkinator`, `mermaid`, and `vega-lite` are CLIs or libraries, not MCP servers.
- Keep shadcn separate from this plugin. Use it only when the user asks for shadcn or when the deliverable is explicitly an app-style implementation.
- Every external helper must keep the generated doc readable as plain HTML. A missing external package must not break the written explainer.

## Source tracking

Tracked external packages live in `tool-finder.update-watch.json`. To refresh the list:

```bash
node scripts/check-tool-updates.mjs
```

To run a broader Tool Finder discovery pass from this plugin root:

```bash
python3 ${TOOL_FINDER_ROOT}/scripts/search_all_providers.py "infographic docs html accessibility shadcn diagrams charts playwright mcp" --root "$PWD" --local-limit 0 --report-dir ./tool-finder-report
```
