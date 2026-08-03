# Tagging a doc

Every document folder gets a `meta.json` (tags + title + description) beside its required `index.html`. A generator inlines all of them into the library index. This file explains how to choose tags. **The live, authoritative tag list is `${KB_ROOT}/tags.json` — read it at doc-creation time; do not duplicate it here.**

## The five dimensions

Each tag belongs to exactly one dimension. A doc should carry tags across several dimensions, not many tags from one.

| Dimension | What it answers | Examples |
|---|---|---|
| `kind` | What *format* is this doc? | `explainer`, `infographic`, `comparison`, `curated-list`, `reference`, `style-guide`, `weekly-update`, `config-map`, `prototype`, `sample` |
| `subject` | What does it *cover*? | `sdk`, `plugin`, `agents`, `skills`, `hooks`, `memory`, `workflows`, `ui-libraries`, `browser-agent`, `feature`, `tool` |
| `platform` | Which *platform*, if any? | `codex`, `claude-code` |
| `topic` | A *named thing* it's about | `portless`, `wshobson`, `shadcn`, `loom`, `infographic-docs` |
| `brand` | Which project or product it maps to | `example-app`, `internal-tools`, `mobile-client` |

## How to choose

1. **Always at least one `kind`.** Pick the format that matches what you built. Multi-format docs can take two (e.g. an `infographic` that is also a `comparison`).
2. **Add the `subject` tags** for what the doc is actually about — usually 1–4.
3. **Add a `platform` tag** only when the doc is specifically about Codex or Claude Code.
4. **Add `topic` tags** for any named tool / product / library the doc centers on. If the named thing has no tag yet, coin one (kebab-case).
5. **`brand` tags are derived for you.** Every project that received a Use Cases sub-page gets its brand tag. **You don't add these by hand** — `tag-doc.mjs` reads the doc's `use-cases-<brand>.html` files and adds them (see *Finalize* below). Adding them manually is harmless; omitting them is fine. A doc with no Use Cases tab usually has no brand tags.

## Reuse before you invent

Prefer an existing tag over a near-synonym. Check `tags.json` first. Only coin a new tag when nothing fits — and when you do:

1. Decide its dimension.
2. Add it to `tags.json` under that dimension **before** the generator runs (otherwise it silently falls back to `subject` and the generator warns).
3. Keep it kebab-case, lowercase, singular-ish, and consistent with the style of existing tags.

## meta.json shape

```json
{
  "title": "What's an SDK?",
  "desc": "Plain-English explainer on SDKs — what they are, a technical deep-dive, and how they apply across your tools.",
  "tags": ["explainer", "sdk", "feature", "example-app"],
  "model": "Claude Opus 4.8",
  "order": 17
}
```

- `title` / `desc` — what shows on the index card. `desc` is one plain-English line.
- `tags` — flat array across dimensions; the index colors/groups them automatically via `tags.json`.
- `model` — which AI model generated the doc, named as the user would recognize it (`Claude Opus 4.8`, `GPT-5 Codex`, …). Write the model you're running as. Shown on the doc footer and the library card.
- `order` — integer controlling card order (use current max + 1 for a new doc).
- `status` — optional, `"draft"` or `"incomplete"`. Omit for finished docs.

Every document entry point is `<folder>/index.html`. Loose HTML files, sidecar `<name>.meta.json` files, and alternate entry-point overrides are not supported.

## Finalize

After writing `meta.json` with your *semantic* tags, run the bundled helper — it adds brand tags from the Use Cases pages, validates every tag against `tags.json`, assigns `order`, and regenerates the index:

```bash
node "$PLUGIN_ROOT/scripts/tag-doc.mjs" <topic-slug>
# preview only, write nothing:
node "$PLUGIN_ROOT/scripts/tag-doc.mjs" <topic-slug> --dry-run
```

(`$PLUGIN_ROOT` is `${CODEX_PLUGIN_ROOT}` in Codex / `${CLAUDE_PLUGIN_ROOT}` in Claude Code. Absolute fallback path: `${CODEX_PLUGIN_ROOT}/scripts/tag-doc.mjs`. `KB_ROOT` overrides the knowledge-base root; `KB_INFO_DOCS` is an explicit document-directory override. The helper still reads `tags.json` and runs `build-index.mjs` from `KB_ROOT`.)

Under the hood the helper calls the repo's own generator, `${KB_ROOT}/build-index.mjs`, which rewrites the data block inside the root `index.html` from every `info-docs/<slug>/meta.json` plus root `tags.json`. That generator is idempotent and zero-dependency; you can run it directly if you only changed `tags.json` or edited a `meta.json` by hand and just need a refresh.
