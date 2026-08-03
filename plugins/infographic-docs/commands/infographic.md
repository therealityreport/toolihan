---
name: infographic
description: Create a multi-page HTML explainer about a topic, in the Codex visual style guide
---

The user wants a multi-page HTML infographic-style explainer about: $ARGUMENTS

Invoke the `infographic-doc` skill from this plugin to produce it. Follow the skill's procedure exactly:

1. Decide the doc folder — always `${KB_ROOT}/info-docs/<topic-slug>/`, where `<topic-slug>` is named for the tool/skill/topic (kebab-case). Then decide the tab list, the brand palette, and the section flow for the main page. The default tab list is Overview / Deep-dive / **Glossary** / Sources — the Glossary defines, in plain English, every term and acronym used in the other tabs — plus a Use Cases tab when the topic is an adoptable tool or library.
2. Copy the skill's `assets/styles.css` into the output `assets/` directory.
3. Copy the skill's `templates/nav-script.js` into the output `assets/` directory.
4. Build each tab as a separate HTML file at the output root, using the page skeleton shown inline in the skill's SKILL.md (Step 4) — fill in title, mark the correct tab `active`, fill `<main>`.
5. Route optional external helpers only when needed: shadcn only when explicitly requested, Mermaid/Vega-Lite only for diagrams or charts, Playwright MCP only for preview proof, and Tool Finder only for discovery/update tracking. See `reference/external-tools.md`.
6. If the doc includes `.mmd` or `.vl.json` files under `visuals/` or `assets/visuals/`, render them with `node "$PLUGIN_ROOT/scripts/render-visuals.mjs" <topic-slug>` before final preview.
7. Tag the doc: read `${KB_ROOT}/tags.json`, pick the *semantic* tags (kind / subject / platform / topic) and write `meta.json` beside the folder's required `index.html` (`{ "title", "desc", "tags" }`). Then run `node "$PLUGIN_ROOT/scripts/tag-doc.mjs" <topic-slug>` — it auto-adds brand tags from the Use Cases pages, validates against the vocabulary, assigns `order`, and runs the root `build-index.mjs`. See the skill's `reference/tagging.md`.
8. Verify the doc folder is under `${KB_ROOT}/info-docs/`, contains both `index.html` and `meta.json`, every page references `assets/styles.css` relatively, every tab bar has exactly one `active` link, prev/next pagination resolves, generated visual assets resolve, and the new doc shows up as a card in `${KB_ROOT}/index.html`.

If the user did not provide a topic, ask them what to explain. **Always save the doc to `${KB_ROOT}/info-docs/<topic-slug>/`** — one folder per doc, named for the tool/skill/topic, with `index.html` and `meta.json`. Do not create loose HTML documents, save to the home directory or cwd, or use a different location unless the user explicitly names one for this doc.

Even for a small topic, ship a multi-page doc — at minimum an Overview tab, a Glossary tab (plain-English definitions of any terms used), and a Sources tab. The plugin's whole identity is multi-page.

Do not use a CSS framework by default. Do not inline the stylesheet in each page. Do not fake tabs with JS visibility toggles. Tabs are real HTML files. Use shadcn only when the user explicitly asks for shadcn or asks for an app-style implementation instead of a standalone doc.
