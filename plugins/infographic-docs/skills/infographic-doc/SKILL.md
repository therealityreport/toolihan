---
name: infographic-doc
description: Use when the user asks for a standalone HTML explainer, guide, infographic, recap, deep-dive, visual summary, or report. Generates a multi-page document with one HTML file per tab, shared navigation, responsive shadcn-inspired styling, accessible typography, dark mode, diagrams, charts, glossary, and sources. Do not use for web applications, live-data dashboards, marketing sites, component demos, or tasks whose deliverable is application code.
---

# Infographic-style HTML explainer

When the user requests an HTML document that explains, summarizes, or visually communicates something, produce a **multi-page HTML document** using the shared style guide bundled with this skill. Do not invent a new design system, do not use a CSS framework, do not output a single all-in-one HTML file.

## External tool routing

The bundled stylesheet remains the default design system. External tools are optional helpers, not new defaults. Route them this way:

- **shadcn**: use only when the user explicitly asks for shadcn or asks for an app-style implementation instead of a standalone doc. Start with `npx shadcn@latest add <components> --dry-run`; keep the standalone HTML path as the default.
- **Playwright MCP**: use only when preview proof, screenshots, PDFs, or browser snapshots are useful. Serve the generated doc folder over localhost and use the `infographic-preview-playwright` MCP server. Do not require MCP for every doc.
- **Mermaid**: use for flows, sequences, state diagrams, timelines, and dependency maps. Inline Mermaid is allowed for editable docs; pre-render to assets when deterministic screenshots/PDFs matter.
- **Vega-Lite / Vega**: use for concise charts from small structured data. Store `.vl.json` specs under `visuals/` or `assets/visuals/`, then render them into doc-local assets.
- **Observable Plot / D3**: use as references for richer chart patterns. Do not make them runtime dependencies unless the doc truly needs live rendering.
- **Tool Finder**: use to refresh the external shortlist or check package drift. The watch list lives at the plugin root in `tool-finder.update-watch.json`.

Read `reference/external-tools.md`, `reference/preview-mcp.md`, and `reference/diagrams-charts.md` before using these helpers.

## Where docs are saved

**Every infographic doc is saved under `${KB_ROOT}/info-docs/`.** This is the fixed home for all infographic docs. Do not save them to the home directory (`~/`), the current working directory, or anywhere else — unless the user explicitly names a different location for a specific doc.

Each doc gets **its own folder** inside `info-docs/`, named for the **tool / skill / topic** it covers (kebab-case). All of that doc's linked HTML files and any other assets live inside that folder.

```
${KB_ROOT}/info-docs/
└── <topic-slug>/           ← one folder per doc, named for the tool/skill/topic
    ├── index.html          ← Tab 1 (the main infographic / overview)
    ├── <tab-2-slug>.html   ← Tab 2 (e.g. changelog.html, deep-dive.html)
    ├── <tab-3-slug>.html   ← Tab 3 (e.g. sources.html)
    ├── ...                 ← Add as many tabs as the content warrants
    ├── meta.json           ← tags/topics + title/desc for this doc (drives the library index)
    └── assets/
        ├── styles.css      ← Copied from this skill's assets/
        └── nav-script.js   ← Copied from this skill's templates/
```

Every doc folder must contain both `index.html` and `meta.json`. Loose HTML files and sidecar metadata are not supported. The doc is registered in the library index at the knowledge-base root `index.html` — but you never hand-edit that file. Root `build-index.mjs` reads each folder's `meta.json` and root `tags.json`, then regenerates the index. See **Step 8** below.

### Folder naming system

Name the doc folder after the subject — the tool, skill, library, or topic being explained — in descriptive kebab-case. The name should make the folder self-identifying when browsing `info-docs/`:

| Subject of the doc | Folder name |
|---|---|
| The Scrapling tool | `scrapling/` |
| The `infographic-doc` skill | `infographic-doc-skill/` |
| Supabase Row-Level Security | `supabase-rls/` |
| Codex weekly updates (May 11) | `codex-weekly-may-11/` |

If a doc about the same subject already exists in `info-docs/`, either update that folder in place or, when the user wants to keep both, add a distinguishing suffix (e.g. a date or version: `scrapling-v2/`). Never overwrite an existing folder without confirming.

**Tabs are separate HTML files**, not anchors in a single document. Each page links to the others via a shared tab bar at the top. Within a page, you can still have scroll-snap "sub-sections" anchored by `id` — that's fine. The rule is: **top-level tabs = separate files**.

## Default tab structure

For most topics, these four tabs are the right default:

1. **Overview** (`index.html`) — the infographic-style narrative: hero, timeline, key sections, impact, get-started. Long-scroll with scroll-snap sections.
2. **Deep-dive / Changelog / Reference** (`<topic>.html`) — long-form prose, lists, tables. Use `.doc-page` + `.changelog-entry` blocks.
3. **Glossary** (`glossary.html`) — plain-English definitions of every term, acronym, and piece of jargon used anywhere in the doc. See **Glossary tab** below. Include it on essentially every doc.
4. **Sources** (`sources.html`) — link cards in `.sources-grid` pointing to citations.

If the topic calls for more or fewer tabs, use your judgment. A weekly recap might add a Releases or platform-specific tab; a tutorial might fold the deep-dive into a Step-by-step tab. But **Glossary and Sources are the two reference tabs that belong on almost every doc.** **Never use anchors-in-one-file just to avoid making more files.**

## Use Cases tab — mandatory when summarizing tools, libraries, SDKs, frameworks, or curated repos

When the source material is a **tool, library, SDK, framework, awesome-list, or any other repo/page whose value is "things you could adopt"**, add a fourth top-level tab:

4. **Use Cases** (`use-cases.html`) — a landing page that lists relevant projects that could adopt items from the source, plus one sub-page per project mapping tools to practical outcomes.

### Hard rules for Use Cases

- **Choose only relevant projects.** Pick up to 3–6 projects whose current workflows would plausibly benefit. Skip projects whose stack or purpose is unrelated.
- **Per-project sub-pages must be specific, not generic.** Name concrete features, real-world scenarios, named entities from the project (show names, league names, screen names, button labels), and outcomes a non-coder would recognize. Phrases like "you could integrate X" are not allowed. Correct level of detail (plain-language): "Right now, when you process this season of Real Housewives, you don't know whether it cost $5 or $50 until the invoice lands. Helicone shows you that number live, per show." File paths, environment variables, function names, and code snippets are NOT allowed in the body — describe what the change accomplishes, not how it's wired.
- **One sub-page per project.** File slug pattern: `use-cases-<project-slug>.html` (kebab-case). Linked from a card on `use-cases.html`.
- **The landing page (`use-cases.html`) cards** show: project name + 1-line description, stack chips, an "N / M SDKs apply" count, a short bullet list of the most relevant items, and a CTA button to the sub-page.
- **Each sub-page ends with a "Suggested rollout order"** — a numbered list ordering the items by adoption cost vs. payoff for THAT project.
- **Wire the new tab into the shared tab bar on every page** with the same `tab-btn` markup, and add it to the prev/next pagination flow (typically: Overview → Deep-dive → Use Cases → Sources).

### When to skip the Use Cases tab

- The source isn't adoptable in a project context (a news event, a film, a person, a historical topic).
- The user explicitly says not to include it.

When in doubt, include a use-case page only when the source material and an available project have a concrete, evidence-backed fit.

## Glossary tab — include on essentially every doc

Every tab must read in plain English (see **Hard rules**), yet most docs unavoidably introduce terms a non-coder hasn't met — product names, acronyms, technical concepts. The **Glossary** tab (`glossary.html`) is where each of those is defined once, plainly. It lets the other tabs use a term, gloss it briefly on first use, and trust the reader can look up the full definition here. Treat it as a standard tab.

It sits near the end, as a reference appendix. The flow is: **Overview → Deep-dive → [Use Cases] → Glossary → Sources.**

Build it with the `.glossary-list` / `.glossary-term` components (see `reference/components.md`) inside a `.doc-page` wrapper.

### Hard rules for the Glossary

- **Cover the terms that actually appear in THIS doc.** Walk the Overview, Deep-dive, and Use Cases tabs and pull every word a non-coder would stumble on — acronyms (API, SDK, LLM, CLI), product/tool names, and concept words ("webhook", "vector database", "rate limit"). Don't pad it with generic terms the doc never uses, and don't leave out a term the doc leans on.
- **Definitions are plain English — the same bar as the rest of the doc.** No code, no file paths, no command syntax. Use the analogy-driven style: "**Webhook** — an automatic message one app fires off to another the moment something happens, like a doorbell that rings a different house." The *term* can be the jargon (that's the whole point of a glossary); the *definition* cannot.
- **Define, don't restate.** "API — an API" is useless. Lead with what it does for the reader, then optionally name it.
- **Order for lookup.** Alphabetical by default. For a doc with natural clusters you may group by category instead (e.g. "Billing terms", "Model terms") using `.glossary-group` + `.gg-letter`. Pick one scheme; don't mix. For a long list, add a `.glossary-index` jump bar at the top.
- **Optionally note where a term shows up** with `.gt-seen` (e.g. "Appears in: Overview, Use Cases") so the reader can jump back to context.
- **Link heavy terms back to the glossary** when it helps — give each `.glossary-term` an `id` (e.g. `id="sdk"`) and point the first inline use at it (`<a href="glossary.html#sdk">SDK</a>`). The inline plain-English gloss on first use is still required; the glossary is the backstop, not a substitute for it.
- **Wire the tab into the shared tab bar on every page** with the `📖 Glossary` `tab-btn`, and add it to the prev/next pagination flow.

### When to skip the Glossary tab

- The doc genuinely uses no term a layperson wouldn't know (rare — a purely narrative recap with no tools, acronyms, or technical concepts).
- The user explicitly says not to include it.

When in doubt, include it. A glossary missing from a jargon-heavy doc is the real failure.

## Step-by-step procedure

**Plugin root.** Several steps below copy bundled files from this plugin. `$PLUGIN_ROOT` means this plugin's install directory — `${CODEX_PLUGIN_ROOT}` when running in Codex, `${CLAUDE_PLUGIN_ROOT}` when running in Claude Code. If neither variable is substituted, read the referenced file directly from this skill's own directory (absolute fallback: `${CODEX_PLUGIN_ROOT}/`).

### 1. Decide the doc structure first

Before writing any HTML, decide:

- The doc folder, which is **always** `${KB_ROOT}/info-docs/<topic-slug>/`. Pick `<topic-slug>` from the tool/skill/topic being explained (kebab-case, descriptive — `scrapling`, `infographic-doc-skill`, `codex-weekly-may-11`, `agent-memory`). Create the folder if it doesn't exist; see "Where docs are saved" above for the naming system and how to handle an existing folder for the same subject.
- The list of tabs (each a separate file). Pick file slugs (e.g. `index.html`, `changelog.html`, `sources.html`).
- The brand palette — see `reference/palettes.md`. Most docs work with the default teal. Pick a different palette only if the topic has a clear brand or visual system.
- The page sections inside the main tab (hero, timeline, etc.) — see `reference/components.md`.

### 2. Copy the stylesheet

Copy this skill's `assets/styles.css` into the output directory's `assets/` folder. Do not inline these styles into each HTML file — the whole point of multi-page is sharing a single stylesheet.

```
DOC_DIR="${KB_ROOT}/info-docs/<topic-slug>"
mkdir -p "$DOC_DIR/assets"
cp "$PLUGIN_ROOT/skills/infographic-doc/assets/styles.css" "$DOC_DIR/assets/styles.css"
```

(If neither `${CODEX_PLUGIN_ROOT}` nor `${CLAUDE_PLUGIN_ROOT}` is substituted, read `assets/styles.css` directly from this skill's directory and write it to the target.)

### 3. Copy the shared JS

Copy this skill's `templates/nav-script.js` into the output directory's `assets/` folder too. It powers fade-up animations and active-state for the right-side nav dots.

```
cp "$PLUGIN_ROOT/skills/infographic-doc/templates/nav-script.js" "$DOC_DIR/assets/nav-script.js"
```

### 4. Build each page from this skeleton

Every tab page uses this skeleton. The only things that change between pages are: the `<title>`, which tab-bar link has `active`, and the contents of `<main>`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DOC_TITLE — TAB_NAME</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/styles.css">
  <!-- NEUTRAL by default — this is the house style, and every reference doc
       ships with NO tint. Leave it neutral: do not add a <style> block here.
       ONLY add a per-doc tint when the user explicitly asks, or the topic has a
       strong brand color. To tint, add exactly:
         <style>:root{ --primary: H S% L%; --ring: H S% L%; }</style>
       (a bare HSL triple, no hsl() wrapper). See reference/palettes.md. -->
</head>
<body>

<!-- Shared tab bar — ONE row, identical on every page; only `active` moves.
     The logo is the mark + the doc title in plain text. There is NO
     description line in the tab bar (the hero-sub carries the one-liner). -->
<div class="tab-bar">
  <a href="index.html" class="tab-bar-logo">
    <span class="logo-mark">XX</span> DOC_TITLE
  </a>
  <a href="index.html" class="tab-btn active">
    <span class="tab-icon">📊</span> Overview
  </a>
  <a href="changelog.html" class="tab-btn">
    <span class="tab-icon">📋</span> Changelog
  </a>
  <a href="glossary.html" class="tab-btn">
    <span class="tab-icon">📖</span> Glossary
  </a>
  <a href="sources.html" class="tab-btn">
    <span class="tab-icon">🔗</span> Sources
  </a>
</div>

<!-- Right-side nav (index.html only): one EMPTY anchor per section. The label
     rides in data-label (rendered by CSS). nav-script.js sets `active` on
     scroll. One anchor href per <section class="page" id="…">. -->
<nav class="page-nav" aria-label="Sections">
  <a href="#hero" data-label="INTRO" class="active"></a>
  <a href="#what" data-label="WHAT CHANGED"></a>
  <a href="#impact" data-label="IMPACT"></a>
  <a href="#start" data-label="GET STARTED"></a>
</nav>

<!-- padding-top clears the fixed single-row tab bar. -->
<main style="padding-top:56px;">

  <!-- HERO — first screen of index.html only. -->
  <section id="hero" class="page hero">
    <div class="page-inner">
      <div class="hero-badge fade-up"><span class="dot"></span> CATEGORY · DATE</div>
      <h1 class="hero-title fade-up stagger-1">
        A short headline,<br>broken by line —<br><em>italics for the key phrase.</em>
      </h1>
      <p class="hero-sub fade-up stagger-2">
        Two plain-English sentences: what this doc covers and why the reader should care.
      </p>
      <div class="hero-stats fade-up stagger-3">
        <div><div class="hero-stat-val">6</div><div class="hero-stat-label">FIRST STAT<br>LABEL</div></div>
        <div><div class="hero-stat-val">3.2×</div><div class="hero-stat-label">SECOND STAT<br>LABEL</div></div>
        <div><div class="hero-stat-val">−40%</div><div class="hero-stat-label">THIRD STAT<br>LABEL</div></div>
        <div><div class="hero-stat-val">100%</div><div class="hero-stat-label">FOURTH STAT<br>LABEL</div></div>
      </div>
    </div>
  </section>

  <!-- CONTENT SECTION — repeat this shape 4–6 times, varying the inner grid
       (.h-grid, .release-grid, .impact-grid, .timeline-wrap, .step-grid …).
       Every section opens with a .page-number eyebrow + .section-title +
       .section-desc, and its <section> id matches a .page-nav anchor above. -->
  <section id="what" class="page">
    <div class="page-inner">
      <div class="page-number">01 — WHAT CHANGED</div>
      <h2 class="section-title">One outcome-focused heading per section</h2>
      <p class="section-desc">A lede sentence framing the cards below in plain English.</p>
      <div class="h-grid">
        <div class="h-card fade-up"><div class="h-icon">📦</div><h4>Card title</h4><p>Plain-English body that leads with the reader's outcome.</p><div class="h-meta">META LABEL</div></div>
        <div class="h-card fade-up stagger-1"><div class="h-icon">↻</div><h4>Card title</h4><p>Body copy.</p><div class="h-meta">META LABEL</div></div>
        <div class="h-card fade-up stagger-2"><div class="h-icon">▦</div><h4>Card title</h4><p>Body copy.</p><div class="h-meta">META LABEL</div></div>
      </div>
    </div>
  </section>

  <!-- … more <section class="page"> blocks (impact, get-started). See
       reference/components.md for every grid type. Use ONLY classes that
       appear there — never invent class names. … -->

  <div class="footer-bar"><p>DOC_TITLE · DATE · MADE WITH MODEL_NAME</p></div>
</main>

<script src="assets/nav-script.js"></script>
</body>
</html>
```

For each tab page:

1. Set `<title>` to `<Doc Title> — <Tab Name>`.
2. Replace `DOC_TITLE` (the plain-text logo title) and the `XX` logo mark — identical on every page — and `MODEL_NAME` in the footer with the model you're running as (see Step 8). The tab bar has **no** description line; the doc's one-liner lives in the hero-sub on `index.html`.
3. In the tab bar, add `class="active"` to the link for THIS page (and only this page).
4. Leave the doc **neutral** (no `<style>` override) — that's the house style and matches every reference doc. Add a `--primary`/`--ring` tint only if the user explicitly asks or the topic has a strong brand color (see `reference/palettes.md`). Never hard-code hex colors into elements.
5. Fill `<main>` with the page's content using **only** component classes from `reference/components.md`. The right-side `<nav class="page-nav">` belongs on `index.html` (the long-scroll overview); secondary pages (changelog/glossary/sources) drop it and use the `.doc-page` wrapper instead.

### 5. Write the main page (`index.html`)

The main page (`index.html`) is **always** the scroll-snap layout — `<main style="padding-top:56px;">` holding `<section class="page">` blocks, the first being `class="page hero"`. **Never** build `index.html` with the `.doc-page` wrapper (that layout is for secondary pages only). It is a **long-scroll of 6–7 full sections**, not a single screen. Pick what fits:

- `<section class="page hero">` — hero with badge, title, sub, and a 4-up `.hero-stats` block
- `<section class="page">` with `.timeline-wrap` — chronological events
- One or more `<section class="page">` with `.release-grid` (two `.release-col` of `.feat-item`) or `.h-grid` — feature blocks
- `<section class="page">` with `.impact-grid` + `.impact-quotes` — stats + pull quotes
- `<section class="page">` with `.step-grid` + `.resource-grid` — get-started CTA + resource links
- `.verdict` callout boxes anywhere you want a one-line takeaway
- `<div class="footer-bar">` at the end

**Fill every section — match the reference docs' density, not a skeleton.** This is the single biggest gap between a doc that reads as "designed by Claude" and one that reads as thin. Concretely:

- **6–7 sections** on the overview (hero + 5–6 content sections). Five is the floor, not the target.
- **At least 3–4 _different_ grid types** across the overview (`.h-grid`, `.release-grid`, `.impact-grid`, `.timeline-wrap`, `.step-grid`) — don't repeat `.h-grid` five times. A doc that leans on one grid type looks half-built.
- **Every content section contains a grid.** A section with only a `.section-desc` + a `.verdict` and no cards is too thin — add a grid.
- **Each `.section-desc` is 2–3 sentences** (≈40–80 words), not one line. Give real context before the grid.
- **Each card body** (`.h-card p`, `.feat-item p`) is **2+ sentences** carrying a concrete detail — a number, a named example, an analogy — not a one-line dictionary definition.
- **Fill each grid to 3–6 cards**, and each `.release-col` to 3–6 `.feat-item`s.
- **Use 2–3 `.verdict` callouts** across the overview to land takeaways (`.verdict.maybe` for caveats, `.verdict.no` for warnings).
- **The final section** ends with a `.step-grid` (get-started) **and** a `.resource-grid` of **4** cards (linking the other tabs / external resources), then the `.footer-bar`.
- Rule of thumb: if `index.html` is under **~15 KB** of markup, it is almost certainly too thin. Open `reference/components.md` and a reference doc (`${KB_ROOT}/info-docs/ponytail-codex-token-savings/`) and match that level of detail.

Include `<nav class="page-nav">` with one **empty** `<a data-label="…">` per section, on the right side. Each section needs a unique `id` that matches its anchor's `href`. (The label is the `data-label` value, rendered by CSS — do not put text inside the anchor.)

### 6. Write secondary pages

Secondary pages use the `.doc-page` layout — a centered max-width column inside a **bare `<main>`** (`.doc-page` already clears the fixed tab bar, so secondary pages need **no** `padding-top` on `<main>`; only `index.html`'s `<main>` takes `style="padding-top:56px;"`). Common patterns:

- **Changelog / detailed reference**: `.changelog-entry` blocks with `.ce-header`, `.ce-tag`, and **at least one `.ce-section`** (a bulleted list) per entry. A bare `.ce-summary` with no `.ce-section` reads as a stub.
- **Glossary**: a `.glossary-list` of `.glossary-term` cards (term + plain-English definition), optionally clustered into `.glossary-group` blocks and fronted by a `.glossary-index` jump bar.
- **Sources / resources**: a `.sources-grid` of **4+** `.source-card` links with substantive descriptions.
- **Step-by-step / tutorial**: vertical stack of `.changelog-entry` blocks, one per step.

**Don't ship skeletal secondary pages.** Each should justify being its own page: multi-sentence bullets, concrete examples, and a `.verdict` where a takeaway helps. A deep-dive or cheat-sheet tab under ~5 KB is probably too thin — expand it or fold it into another tab.

**Pagination follows the tab-bar order exactly.** Walk the tab bar left-to-right: each page's `← PREVIOUS` points to the tab immediately to its **left** and `NEXT →` to the tab immediately to its **right** — never skip a tab back to `index.html`. (With tabs Overview → Cheat Sheet → Examples → Glossary → Sources, the **Examples** page's PREVIOUS is **Cheat Sheet**, not Overview.) The Overview page carries no pagination; the last tab omits NEXT. Always include the arrow glyphs (`← PREVIOUS`, `NEXT →`), and keep pagination **within this doc** — never link a sibling doc here.

End every secondary page with the `.page-pagination` block, a `.footer-bar`, and — like **every** page — `<script src="assets/nav-script.js"></script>` immediately before `</body>`.

### 7. Render optional diagram and chart assets

If the doc uses Mermaid diagrams or Vega-Lite chart specs, keep the source files inside the doc folder:

```
<doc-folder>/visuals/<diagram>.mmd
<doc-folder>/visuals/<chart>.vl.json
```

Then render them into doc-local assets:

```bash
node "$PLUGIN_ROOT/scripts/render-visuals.mjs" <topic-slug>
```

The script writes generated assets under:

```
<doc-folder>/assets/generated/
```

Use this for deterministic screenshots, PDFs, and offline-friendly docs. If you use inline Mermaid instead, include the Mermaid module snippet only on pages with Mermaid blocks and summarize the diagram in plain English nearby.

### 8. Tag the doc and refresh the library index

Every doc is registered in the root library index (`${KB_ROOT}/index.html`) through a per-folder metadata file — you do **not** hand-edit the index, and a bundled helper does the mechanical tagging for you. After the pages exist:

1. **Read the tag vocabulary** at `${KB_ROOT}/tags.json` — the controlled list of tags grouped into five dimensions (`kind`, `subject`, `platform`, `topic`, `brand`). Reuse existing tags wherever they fit.
2. **Pick the doc's _semantic_ tags** (full method in `reference/tagging.md`):
   - one or more **kind** tags for the doc's format (`explainer`, `infographic`, `comparison`, `curated-list`, `reference`, `style-guide`, `weekly-update`, `config-map`, `prototype`, `sample`);
   - the **subject** tags for what it covers;
   - a **platform** tag (`codex` / `claude-code`) when the doc is about one;
   - **topic** tags for named things (a tool / product / library referred to by name).
   - You do **not** need to add **brand** tags by hand — the helper derives them from the doc's Use Cases pages in the next step (adding them anyway is harmless).
   - Only coin a new kebab-case tag when nothing fits; when you do, add it to `tags.json` under the right dimension *first*.
3. **Write `meta.json`** in the doc's folder with those semantic tags and the generating model:
   ```json
   { "title": "<doc title>", "desc": "<one-line plain-English summary>", "tags": ["explainer", "…"], "model": "Claude Opus 4.8" }
   ```
   - `"model"` records **which AI model produced this doc**, so the library shows at a glance whether Claude or Codex (and which version) built each infographic. Name yourself the way the user would recognize you — `Claude Opus 4.8`, `Claude Sonnet 4.6`, `GPT-5 Codex`, `Codex`. Use the model you are **currently running as**; if you only know the family, use that. Don't claim to be a model you aren't.
   - Add `"status": "draft"` or `"status": "incomplete"` only when relevant. Always keep this metadata in the document folder beside its required `index.html`.
4. **Finalize + index it** with the bundled helper:
   ```bash
   node "$PLUGIN_ROOT/scripts/tag-doc.mjs" <topic-slug>
   ```
   (`$PLUGIN_ROOT` is `${CODEX_PLUGIN_ROOT}` in Codex / `${CLAUDE_PLUGIN_ROOT}` in Claude Code.) The helper adds **brand** tags from the doc's `use-cases-<brand>.html` pages, validates every tag against root `tags.json`, assigns `order`, writes `meta.json` back, and runs root `build-index.mjs`. `KB_ROOT` defaults to `./knowledge-base`; `KB_INFO_DOCS` remains an explicit helper override for the document directory. If it warns that a tag isn't in `tags.json`, add it there under the right dimension and re-run. Pass `--dry-run` to preview without writing.

### 9. Preview with Playwright MCP when warranted

If the doc includes generated visual assets, complex responsive layout, or the user asks for preview proof:

1. Start a local static server from the generated doc folder:
   ```bash
   python3 -m http.server 8765
   ```
2. Open `http://localhost:8765/index.html` through the `infographic-preview-playwright` MCP server.
3. Capture screenshots, snapshots, or PDF output only when they materially help prove the doc is usable.

Prefer localhost previews over `file://` previews. The bundled MCP config does not grant unrestricted file access.

### 10. Verify

After writing all pages:

- Confirm the doc folder lives at `${KB_ROOT}/info-docs/<topic-slug>/` (not the home dir or cwd), is named for the tool/skill/topic, and contains `index.html` plus `meta.json`.
- Confirm every page has `<link rel="stylesheet" href="assets/styles.css">` (relative path, no leading slash) and the **Geist + JetBrains Mono** font link (no Instrument Serif / DM Sans).
- **Confirm no undefined classes.** Every class used in every page must be defined in `assets/styles.css`, or it renders unstyled. Check mechanically — from the doc folder:
  ```bash
  comm -23 \
    <(grep -ohE 'class="[^"]+"' *.html | sed -E 's/class="//;s/"//' | tr ' ' '\n' | sort -u) \
    <(grep -oE '\.[a-zA-Z][a-zA-Z0-9_-]+' assets/styles.css | sed 's/\.//' | sort -u)
  ```
  Anything printed (other than state hooks like `active`, `visible`, `next`, `dot`, `stagger-1`…`stagger-5`) is an invented/unstyled class — fix it before finishing.
- **Confirm every page loads the script.** `grep -L 'nav-script.js' *.html` must print nothing — every page (not just `index.html`) needs `<script src="assets/nav-script.js"></script>` before `</body>`.
- **Confirm the overview is the rich scroll-snap layout, not a stub.** `index.html` has one `<section class="page hero">` and **5+** more `<section class="page">` blocks (never the `.doc-page` wrapper), uses **3+ different grid types**, and has **2+ `.verdict`** callouts. If `index.html` is under ~15 KB, it's too thin — enrich it before finishing.
- **Confirm card metadata matches its parent** — `.h-meta` inside `.h-card` (not `.tl-tags`/`.tl-tag`), and every `.resource-grid` holds 4 cards.
- **Confirm pagination matches tab order.** Walk the tab bar left-to-right: each secondary page's `← PREVIOUS` is the tab to its left and `NEXT →` the tab to its right (no skips back to `index.html`), arrow glyphs are present, and no pagination link points outside this doc.
- Confirm exactly ONE tab in each page's tab bar has `class="active"` — and it points to that page.
- Confirm the Glossary tab exists (unless the doc has no specialized terms) and defines every acronym, tool name, and concept the other tabs lean on — each in plain English, no code or jargon in the definitions.
- Confirm all internal links (tab bar, prev/next, anchor dots, any `glossary.html#term` links) actually resolve.
- Confirm generated diagram/chart assets exist under `assets/generated/` when the doc references them.
- Confirm `meta.json` exists in the doc folder and is valid JSON (has `title`, `desc`, `tags`, `model`) — and that the `.footer-bar` on every page ends with `· MADE WITH <model>` naming the same model.
- Confirm `tag-doc.mjs` ran clean (`0 unknown tags`, brand tags present for any Use Cases pages) and the new doc now appears as a card in the library `index.html`.
- Open `index.html` in the user's preview pane if available.

### 11. Commit the changes

Always commit the work this skill produces — a brand-new doc **and** any later edits the user asks for — without waiting to be asked each time. The user has given standing approval for these commits.

- Commit **only the files this skill touched**: the doc folder under `info-docs/<topic-slug>/`, plus root `index.html` and root `tags.json` when regenerated or changed. Stage those paths explicitly; never `git add -A`. Leave the user's other unrelated working-tree changes alone.
- If the repo is on its default branch (`main`/`master`), create a topic branch first (e.g. `docs/<topic-slug>`), then commit there. Otherwise commit on the current branch.
- Write a concise, descriptive message naming the doc and what changed (new doc, added tab, revised section).
- Do **not** push unless the user asks. If pre-existing edits to `index.html`/`tags.json` are entangled with the registration changes, commit them anyway (they're needed for the doc to appear) and note it in your summary.
- After committing, report the branch and the short commit hash.

## Hard rules

- **Plain English throughout.** The entire document — every tab, every card, every caption — must be written so a non-coder can understand it.
  - No code blocks. No file paths. No environment variable names. No CLI commands. No package names like `@e2b/sdk` or `pnpm install`.
  - No jargon without an immediate plain-English gloss. "API" → "a way for two programs to talk to each other (an API)" on first use, then drop it.
  - Use analogies and comparisons liberally. "Like a phone bill itemized by show." "Like watching the replay of a confusing referee call." "Like Tinder for clothing listings."
  - Concrete examples beat abstract ones. Not "track cost" — "see that listing 200 shirts cost you $3.40, broken down per shirt." **Every card body should carry at least one concrete detail** — a number, a named example, an analogy, or a real-world scenario — not a generic textbook line ("You own part of a company"). Lead with what the reader would actually experience.
  - Prefer bullet points over paragraphs for any list of ≥3 items.
  - Short sentences. 6th-grade reading level where possible. Active voice.
  - When summarizing a tool's value, lead with the *outcome* the user gets, not the technical mechanism. "You'll know which show is costing you the most in AI fees" — not "It instruments your LLM calls."
- **One stylesheet, shared across pages.** Never inline the full CSS in each HTML file.
- **Tabs are separate files.** Never use `display: none` + JS toggles to fake tabs across content the user thinks of as separate pages.
- **No CSS frameworks** by default. No Tailwind, Bootstrap, daisyUI, shadcn, etc. The shared stylesheet is the entire design system. **Exception:** if the user explicitly asks for a specific framework (e.g., "use shadcn"), follow their request — but the plain-English rule above still applies regardless of styling.
- **Two type families only:** **Geist** (headings, body, hero/impact numerics — weights 300–700) and **JetBrains Mono** (eyebrows, labels, stat captions, code, `.page-number`, `.tl-tag`). Load exactly the bundled Google Fonts link. Never reintroduce Instrument Serif, DM Sans, or any other face — those belong to the retired style.
- **Use only class names that exist in the stylesheet.** Every element must use a class documented in `reference/components.md` (and therefore defined in `assets/styles.css`). **Do not invent class names.** An undefined class renders as raw, unstyled HTML and is the single most common way these docs come out looking broken. Known traps and their correct equivalents:
  - hero metrics → `.hero-stats` › `.hero-stat-val` + `.hero-stat-label` (never `stat-grid`/`stat-card`/`stat-number`/`stat-label`)
  - section eyebrow → `.page-number` (never `section-kicker`)
  - right-side nav → `<nav class="page-nav">` with empty `<a data-label="…">` (never `.nav-dot` with a `<span>` inside)
  - two-column feature blocks → `.release-grid` › `.release-col` › `.feat-item` (never `.release-card`)
  - main wrapper → `<main style="padding-top:56px;">` on `index.html`; secondary pages use a **bare `<main>`** (the `.doc-page` wrapper clears the bar). The old `.doc-main` class is gone.
  - card metadata → `.h-meta` inside `.h-card` (never `.tl-tags`/`.tl-tag`, which belong to `.tl-event` timeline cards). Match each metadata element to its parent: `.h-meta`→`.h-card`, `.tl-tags`→`.tl-event`, `.ce-tag`→`.ce-header`.
  - `.resource-grid` is a **4-column** layout — fill it with **4** cards (or 8). 3 or 5 cards leave a visible gap.
  - If you genuinely need a layout the components don't cover, compose existing classes — don't coin a new one.
- **Build it rich, not skeletal.** Hit the density targets in Step 5: 6–7 overview sections, 3–4 _different_ grid types, every section with a filled grid (3–6 cards) and a 2–3-sentence `.section-desc`, 2-sentence card bodies, and 2–3 `.verdict` callouts. An `index.html` under ~15 KB of markup is almost always too thin. Secondary pages are full pages too — not bullet stubs. Thin, one-screen docs that leave most of the design system unused are a failure mode, not a minimal-viable success.
- **Stamp the generating model.** Record which model built the doc — your own currently-running model — in the `.footer-bar` of every page (`· MADE WITH <model>`) and in `meta.json` (`"model": "<model>"`). Name it as the user would recognize it (`Claude Opus 4.8`, `GPT-5 Codex`, …). This is how the library shows whether Claude or Codex produced each infographic.
- **No emoji-laden marketing prose.** Emojis are fine as icon glyphs inside `.tl-dot`, `.h-icon`, `.feat-icon`, `.res-icon` — that's their job. Do not pepper them into body copy.
- **Default to the neutral palette.** Ship docs **neutral** — no `--primary` override — like every reference doc; the near-black primary plus the auxiliary `--accent-*` tokens (for variety in lists/grids) are the house style. A colored `--primary`/`--ring` tint is the **exception**, added only on explicit request or a strong brand color — never by default, and never a different tint per doc in a family. Never hard-code hex colors onto elements or introduce new colors mid-doc.
- **Don't over-animate.** The stylesheet's fade-up is enough. Don't add bespoke `@keyframes` unless the topic genuinely needs them.

## Reference files

For details, see:

- `reference/palettes.md` — preset palettes (Codex teal, Anthropic warm, OpenAI mono, AWS orange, etc.) and how to roll a new one.
- `reference/components.md` — every component class with a minimal example.
- `reference/multi-page.md` — exact wiring for the tab bar, prev/next pagination, and active states across pages.
- `reference/tagging.md` — the five tag dimensions and how to pick a doc's tags + write its `meta.json` (Step 8).
- `reference/external-tools.md` — when to route to shadcn, Playwright MCP, Mermaid, Vega-Lite, validation tools, or Tool Finder.
- `reference/preview-mcp.md` — Playwright MCP preview workflow and localhost-first safety rules.
- `reference/diagrams-charts.md` — Mermaid and Vega-Lite source-file conventions plus render commands.

In `templates/`:

- `nav-script.js` — fade-up observer + `.page-nav` active-state observer (plus optional interactive-tab and copy-button helpers). Copy verbatim into each output's `assets/` directory.

(The HTML page skeleton lives inline in Step 4 above — there's no separate template file because a fragment file with no `<head>` renders as unstyled junk when previewed standalone.)

## Examples

Two reference docs in the library show the target quality — study them before generating:

- **`${KB_ROOT}/info-docs/infographic-shadcn-style-guide/`** — the living style guide: every component class rendered with the canonical shadcn/Geist tokens. This is the source of truth that `assets/styles.css` is bundled from.
- **`${KB_ROOT}/info-docs/ponytail-codex-token-savings/`** — a full multi-page explainer (Overview → How-It-Works → Use Cases → Sources) that shows the expected density, plain-English voice, and section flow.

Match their richness and class usage. Do **not** create or copy loose single-file docs; that output mode is retired.
