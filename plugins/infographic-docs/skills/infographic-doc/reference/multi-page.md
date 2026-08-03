# Multi-page wiring

The whole reason this plugin exists: top-level tabs are **separate HTML files**, not anchors on one giant file. This doc explains exactly how to wire that up.

## The file layout

The doc folder always lives inside `${KB_ROOT}/info-docs/`, named for the tool/skill/topic (see SKILL.md → "Where docs are saved"). Inside that folder:

```
${KB_ROOT}/info-docs/<doc-name>/
├── index.html            ← Tab 1 (always named index.html)
├── meta.json             ← Required library metadata
├── <slug-2>.html         ← Tab 2 (kebab-case slug)
├── <slug-3>.html         ← Tab 3
├── ...                   ← One file per tab
└── assets/
    ├── styles.css        ← Shared stylesheet (copied from the plugin)
    └── nav-script.js     ← Shared client script (copied from the plugin)
```

All HTML files sit at the same directory level. The `assets/` directory is referenced via relative path: `<link rel="stylesheet" href="assets/styles.css">`, `<script src="assets/nav-script.js"></script>`.

**Never use leading slashes.** `/assets/styles.css` breaks when the doc is opened from the filesystem (file://) or hosted under a sub-path. Always `assets/styles.css`.

## The shared tab bar

The same `<div class="tab-bar">` lives at the top of every page — a **single row**: the logo (`.logo-mark` + the doc title in plain text) on the left, the `.tab-btn` links after it. The only thing that changes between pages is which `<a class="tab-btn">` has `active`. There is no description line in the tab bar (the doc's one-liner lives in the hero-sub on `index.html`).

Example four-tab doc — here's the tab bar as it appears in each file:

### `index.html` (Overview tab — active)
```html
<div class="tab-bar">
  <a href="index.html" class="tab-bar-logo">
    <span class="logo-mark">Cx</span> Doc Title
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
```

### `changelog.html` (Changelog tab — active)
```html
<div class="tab-bar">
  <a href="index.html" class="tab-bar-logo">
    <span class="logo-mark">Cx</span> Doc Title
  </a>
  <a href="index.html" class="tab-btn">
    <span class="tab-icon">📊</span> Overview
  </a>
  <a href="changelog.html" class="tab-btn active">
    <span class="tab-icon">📋</span> Changelog
  </a>
  <a href="glossary.html" class="tab-btn">
    <span class="tab-icon">📖</span> Glossary
  </a>
  <a href="sources.html" class="tab-btn">
    <span class="tab-icon">🔗</span> Sources
  </a>
</div>
```

### `glossary.html` (Glossary tab — active)
```html
<div class="tab-bar">
  <a href="index.html" class="tab-bar-logo">
    <span class="logo-mark">Cx</span> Doc Title
  </a>
  <a href="index.html" class="tab-btn">
    <span class="tab-icon">📊</span> Overview
  </a>
  <a href="changelog.html" class="tab-btn">
    <span class="tab-icon">📋</span> Changelog
  </a>
  <a href="glossary.html" class="tab-btn active">
    <span class="tab-icon">📖</span> Glossary
  </a>
  <a href="sources.html" class="tab-btn">
    <span class="tab-icon">🔗</span> Sources
  </a>
</div>
```

### `sources.html` (Sources tab — active)
```html
<div class="tab-bar">
  <a href="index.html" class="tab-bar-logo">
    <span class="logo-mark">Cx</span> Doc Title
  </a>
  <a href="index.html" class="tab-btn">
    <span class="tab-icon">📊</span> Overview
  </a>
  <a href="changelog.html" class="tab-btn">
    <span class="tab-icon">📋</span> Changelog
  </a>
  <a href="glossary.html" class="tab-btn">
    <span class="tab-icon">📖</span> Glossary
  </a>
  <a href="sources.html" class="tab-btn active">
    <span class="tab-icon">🔗</span> Sources
  </a>
</div>
```

## Choosing tab slugs

Use kebab-case. Always include the file extension. Keep them short.

| Tab name | File slug |
|---|---|
| Overview | `index.html` |
| Full Changelog | `changelog.html` |
| Glossary | `glossary.html` |
| Sources | `sources.html` |
| Deep Dive | `deep-dive.html` |
| Get Started | `get-started.html` |
| Examples | `examples.html` |
| Reference | `reference.html` |
| Timeline | `timeline.html` |
| Architecture | `architecture.html` |
| Comparison | `comparison.html` |

The first tab is **always** `index.html` so the doc opens cleanly when you visit the directory.

## Prev/next pagination

At the bottom of each secondary tab, add a prev/next link block so the reader can advance without going back to the tab bar. The default reading order is **Overview → Deep-dive/Changelog → [Use Cases] → Glossary → Sources**, so each block links to its neighbours in that flow. Example for the Changelog tab:

```html
<div class="page-pagination">
  <a href="index.html">
    <div class="pp-label">← PREVIOUS</div>
    <div class="pp-title">Overview</div>
  </a>
  <a href="glossary.html" class="next">
    <div class="pp-label">NEXT →</div>
    <div class="pp-title">Glossary</div>
  </a>
</div>
```

Don't put pagination on `index.html` — its hero already serves that role. The user lands there.

**Pagination must follow the tab-bar order exactly.** `← PREVIOUS` points to the tab immediately to the **left** of the current page and `NEXT →` to the tab immediately to the **right**. The most common mistake is linking `← PREVIOUS` back to `index.html` from a page that isn't second in the order — that silently skips a tab. With tabs `Overview → Cheat Sheet → Examples → Glossary → Sources`, the **Examples** page's PREVIOUS is **Cheat Sheet** (not Overview) and its NEXT is **Glossary**. Keep the arrow glyphs and link only within this doc.

## Sub-pages (optional, advanced)

Most docs are fine with one HTML file per top-level tab and a long scroll inside each. If a tab gets too long (more than ~12 scroll-snap sections), you can split it further:

```
<doc-name>/
├── index.html
├── changelog/
│   ├── index.html       ← chronological summary
│   ├── 0-130.html       ← deep dive on one release
│   └── 0-129.html
├── sources.html
└── assets/
    └── styles.css
```

In that case:
- The top-level tab bar's `<a href="changelog/index.html">` points into the sub-directory's index.
- The sub-directory's index has its own sub-tab bar (or just a list of links) to its children.
- The shared stylesheet is still at the root `assets/styles.css`; sub-directory pages reference it as `../assets/styles.css`.

Don't do this unless the content genuinely needs it. Multi-level navigation gets confusing quickly.

## Active-state checklist (every page)

Before declaring a multi-page doc done, verify in each file:

- [ ] `<link rel="stylesheet" href="assets/styles.css">` is present (relative, no leading slash).
- [ ] `<script src="assets/nav-script.js"></script>` is present before `</body>` — on **every** page, secondary tabs included (`grep -L 'nav-script.js' *.html` should print nothing).
- [ ] Exactly ONE `<a class="tab-btn">` has `active` in its class list, and it `href`s to THIS file.
- [ ] The `<title>` tag is set to `<Doc Title> — <Tab Name>`.
- [ ] Internal anchor links (`href="#hero"`) match real `id`s on the page.
- [ ] `.page-pagination` follows the tab-bar order — `← PREVIOUS`/`NEXT →` point to the adjacent tabs (no skipped tabs, no links outside this doc), arrows included, and the `href`s resolve.

## Anti-patterns

- **Don't** use `<script>` to toggle tabs via `display: none`. The whole point of multi-page is real navigation, real URLs, real browser back-button behavior.
- **Don't** inline the full CSS in every page. Shared `assets/styles.css` is the only correct answer.
- **Don't** put `<base href="...">` in `<head>`. It breaks when the doc moves.
- **Don't** use `target="_blank"` on tab-bar links. Tabs are within-doc navigation, not external.
- **Don't** add a "back to top" link — the tab bar is sticky, the page-nav dots are sticky, neither needs a third stickyism.
