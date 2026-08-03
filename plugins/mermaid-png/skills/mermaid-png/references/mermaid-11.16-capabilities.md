# Mermaid 11.16 capability guide

Use this reference to select supported Mermaid 11.16 syntax. All examples are in the plugin-root `examples/11.16/` directory and are render-smoke-tested by `npm run test:smoke`.

## Decision, process, grammar, and hierarchy

- `cynefin-beta` maps work across the clear, complicated, complex, chaotic, and confusion domains. Keep item lists short. Set `cynefin.seed` to a non-zero number for a repeatable boundary shape.
- `swimlane-beta` is a standalone, flowchart-like process diagram. Use `subgraph` blocks as lanes and ordinary flowchart nodes/edges inside them.
- Railroad diagrams are beta and notation-specific: `railroad-beta` for Mermaid IR constructors, `railroad-ebnf-beta`, `railroad-abnf-beta`, and `railroad-peg-beta`. Do not mix their assignment or choice operators.
- `treeView-beta` accepts indented trees or Unicode box drawing (`├──`, `└──`, `│`). A trailing `/` marks a directory. `:::highlight` and `## description` are local annotations; avoid remote icon pack configuration unless requested.

## Charts

- Pie charts accept `pie.donutHole` from `0` through `0.9`, `pie.legendPosition` (`top`, `bottom`, `left`, `right`, or `center`), and `pie.highlightSlice` in front matter. Match the highlight string to a slice label.
- XY line points can contain a numeric value followed by an optional quoted label, such as `line [25 "Launch", 45]`. `xyChart.xAxis.labelRotation` controls bottom-axis rotation. `xyChart.showDataLabel` affects bar values, not line-point labels.

## Layout, models, and schedules

- In `architecture-beta`, `align row a b c` shares a row and `align column a b c` shares a column. Do not contradict an edge's direction with an alignment order. `architecture.seed` gives a reproducible layout; `0` opts out.
- ER attribute types may end in `?` for nullable fields. Use backticks around attribute names or types that contain special characters.
- Gantt permits multiple `excludes` lines; Mermaid combines their tokens. Keep a comment above a long date exclusion group so later readers know why it exists.

## Rendering boundaries

- The local renderer supports PNG and SVG. Output filenames must end in `.png` or `.svg`; an optional explicit format must match the extension. Mermaid CLI also supports other formats, but this plugin exposes only the formats it validates.
- Beta syntax can change upstream. Preserve the exact Mermaid and CLI versions in `package.json`, and rerun the fixture smoke test after upgrading either.
- Do not pass arbitrary Puppeteer arguments through the renderer. The wrapper owns the supported rendering options.
