---
name: mermaid-png
description: Render pasted Mermaid diagram text or .mmd files to PNG or SVG images using Mermaid 11.16, including Cynefin, swimlane, railroad grammar, TreeView, data-chart, architecture, ER, and Gantt diagrams.
---

# Mermaid PNG

Use this skill when the user wants a Mermaid diagram rendered as an image, including PNG, SVG, or both.

Use Mermaid 11.16 diagram routing when it makes the result clearer:

- **Cynefin** for a decision or work item classified as clear, complicated, complex, chaotic, or unknown.
- **Swimlane** for a process owned by two or more teams or roles.
- **Railroad** for EBNF, ABNF, PEG, or a hand-authored grammar structure.
- **TreeView** for a repository, file tree, or other hierarchy.
- **Pie or XY chart** for a small distribution or numerical comparison.
- **Architecture** for service topology; use alignment directives only when the requested spatial grouping matters.
- **ER or Gantt** for a data model or schedule.

Read [the Mermaid 11.16 capability reference](references/mermaid-11.16-capabilities.md) before using a beta diagram type or a newer syntax feature. The plugin-root examples under `examples/11.16/` are render-tested starting points.

## Inputs

- For pasted Mermaid, save the diagram text to a temporary `.mmd` file before rendering.
- For an existing diagram file, use the provided `.mmd` path directly.
- If the user does not specify a format, choose a `.png` output path by default.
- If the user asks for SVG, create an SVG. If they ask for both, run the renderer once per output file.
- Use a clear output filename near the requested destination when one is given. Otherwise, place the image next to the input `.mmd` file.

## Render Command

Run the plugin-local renderer from the mermaid-png plugin root (the directory containing `scripts/render-mermaid.mjs`):

```bash
node scripts/render-mermaid.mjs --input <diagram.mmd> --output <diagram.png|diagram.svg> [--format png|svg] [--theme default] [--background white] [--width 1600]
```

Defaults:

- `format`: inferred from the required `.png` or `.svg` output extension. If supplied, `--format` must match that extension and is forwarded to Mermaid CLI.
- `theme`: `default`
- `background`: `white`
- `width`: `1600`

The renderer honors `PUPPETEER_EXECUTABLE_PATH` when the host needs a specific Chrome binary. On macOS it uses the installed Google Chrome application when no path is set. On another host without a compatible browser, install the browser required by the pinned Mermaid CLI/Puppeteer version before rendering; do not work around this with arbitrary Puppeteer launch arguments.

## Mermaid 11.16 Capabilities

- Keep beta keywords exactly as shown: `cynefin-beta`, `swimlane-beta`, `treeView-beta`, and the four `railroad-*-beta` forms.
- For stable asset checks, set a non-zero `cynefin.seed` or `architecture.seed` in Mermaid front matter. Do not claim visual pixel equality across different Mermaid or browser versions.
- TreeView can accept a familiar box-drawing file tree. Do not add remote Iconify packs merely to render a tree; use labels, annotations, and the built-in `highlight` class unless the user explicitly requests an icon configuration.
- Pie donut/legend/highlight and XY labels/rotation are configured in front matter; preserve that front matter when rendering pasted input.
- Mermaid CLI renders these diagrams through the same generic renderer. This plugin intentionally does not create one MCP tool per diagram type.

## Validation

After rendering, verify the output before reporting success:

- The output file exists and is non-empty.
- PNG output starts with the PNG magic bytes and has readable dimensions via `file` or `sips`.
- SVG output is text/XML and contains an `<svg` element.
- For beta diagrams, render the matching example first when changing syntax, then render the requested source.
- If rendering fails, report the exact command and the important error text instead of claiming an image was created.

## Report Back

In the final response, include the absolute path of each created image. If temporary `.mmd` input files were created only to render pasted text, remove them unless the user asked to keep them.

## Publishing Safety

Treat rendered SVG as an active document. Before publishing an SVG from an untrusted or pasted source, review it for unexpected links, labels, and embedded markup. PNG is the safer default for untrusted diagrams.
