# Diagrams and charts

Use visual helpers when they make the explanation easier to understand. Keep the body text plain English and do not make the reader understand implementation details.

## Mermaid diagrams

Use Mermaid for simple flows, sequences, state machines, timelines, and dependency maps.

### Inline browser-rendered diagram

Add this only on pages that contain Mermaid blocks:

```html
<pre class="mermaid">
flowchart TD
  A[Input] --> B[Decision]
  B --> C[Output]
</pre>

<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({ startOnLoad: true });
</script>
```

Use inline Mermaid when the doc must stay easy to edit and an external CDN is acceptable.

### Pre-rendered diagram asset

Place source diagrams here:

```text
<doc-folder>/visuals/<name>.mmd
```

Then run:

```bash
node ${CODEX_PLUGIN_ROOT}/scripts/render-visuals.mjs <topic-slug>
```

This writes:

```text
<doc-folder>/assets/generated/<name>.svg
```

Use pre-rendered assets when the final doc should not depend on a CDN or when you need screenshots/PDFs to be deterministic.

## Vega-Lite charts

Use Vega-Lite for small charts where the data can be represented by a concise JSON spec.

Place chart specs here:

```text
<doc-folder>/visuals/<name>.vl.json
```

Then run:

```bash
node ${CODEX_PLUGIN_ROOT}/scripts/render-visuals.mjs <topic-slug>
```

The script uses `npx -p vega -p vega-lite vl2svg` by default and writes SVG assets under `assets/generated/`.

## Chart selection

- Use a bar chart for ranked comparisons.
- Use a line chart for change over time.
- Use a small multiple when one chart would hide important groups.
- Use Mermaid instead of a chart when the point is workflow, sequence, ownership, or dependency.
- Use a table when exact values matter more than shape.

## Constraints

- Do not put raw data, implementation commands, or package names in the user-facing body unless the doc is explicitly for developers.
- Cite chart data in the Sources tab.
- Add alt text or a nearby plain-English summary for every chart or diagram.
- Keep generated assets inside the doc folder, usually under `assets/generated/`.
