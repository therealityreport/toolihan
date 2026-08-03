# Component recipes

Every CSS class in `styles.css` shown here with a minimal HTML example. Compose these to build pages.

**This is the allowlist.** These are the only class names the stylesheet styles. If a class isn't here, it isn't in `styles.css`, and it will render as raw unstyled HTML. Build pages by composing these recipes — **never invent a class name** (no `stat-grid`, `section-kicker`, `nav-dot`, `release-card`, `doc-main`, etc.). When you need a layout that isn't here, combine existing classes rather than coining a new one. Type is **Geist** (Sans) + **JetBrains Mono** only.

## Page wrapper (scroll-snap section)

The unit a `.page-nav` dot points to. One per anchor section.

```html
<section id="hero" class="page">
  <div class="page-inner">
    <div class="page-number">01 — INTRO</div>
    <h2 class="section-title">Your section heading</h2>
    <p class="section-desc">Lede paragraph. Two sentences max.</p>

    <!-- section content -->
  </div>
</section>
```

## Doc page wrapper (long-form, no scroll-snap)

For secondary tabs only (changelog / cheat-sheet / examples / glossary / sources). It goes inside a **bare `<main>`** — `.doc-page` already adds the top padding that clears the fixed tab bar, so secondary pages need **no** `padding-top` on `<main>` (only `index.html`'s `<main>` takes `style="padding-top:56px;"`).

```html
<main>
  <div class="doc-page">
    <div class="doc-hero">
      <h1>Tab title</h1>
      <p>One-sentence intro to this tab's content.</p>
    </div>

    <!-- doc content: .changelog-entry blocks, .sources-grid, etc. -->
    <!-- end with .page-pagination + .footer-bar -->
  </div>
</main>
<script src="assets/nav-script.js"></script>   <!-- REQUIRED on every page, secondary ones too -->
```

> **`index.html` NEVER uses `.doc-page`.** The overview is always the scroll-snap `<section class="page">` layout starting with a `.page hero` (see Hero, below). `.doc-page` flattens it into a plain column with no hero — only use it on secondary tabs.

## Hero (first page of the first tab)

```html
<section id="hero" class="page hero">
  <div class="page-inner">
    <div class="hero-badge fade-up">
      <span class="dot"></span> CATEGORY · DATE
    </div>
    <h1 class="hero-title fade-up stagger-1">
      Short headline,<br>break by line —<br><em>italic for emphasis</em>
    </h1>
    <p class="hero-sub fade-up stagger-2">
      Two-sentence subtitle that explains what this doc is.
    </p>
    <div class="hero-stats fade-up stagger-3">
      <div>
        <div class="hero-stat-val">42</div>
        <div class="hero-stat-label">FIRST STAT LABEL<br>TWO LINES MAX</div>
      </div>
      <div>
        <div class="hero-stat-val">3.2×</div>
        <div class="hero-stat-label">SECOND STAT</div>
      </div>
      <!-- Add 2-4 stats total -->
    </div>
  </div>
</section>
```

## Right-side nav dots (one per section)

```html
<nav class="page-nav">
  <a href="#hero" data-label="INTRO" class="active"></a>
  <a href="#timeline" data-label="TIMELINE"></a>
  <a href="#impact" data-label="IMPACT"></a>
</nav>
```

The `nav-script.js` updates `.active` automatically as sections enter the viewport.

## Timeline (chronological events)

```html
<section id="timeline" class="page">
  <div class="page-inner">
    <div class="page-number">01 — TIMELINE</div>
    <h2 class="section-title">What happened, in order</h2>

    <div class="timeline-wrap">
      <div class="tl-event">
        <div class="tl-dot">📦</div>
        <div class="tl-card">
          <div class="tl-date">May 6 · LABEL</div>
          <h4>Event title</h4>
          <p>One-paragraph description.</p>
          <div class="tl-tags">
            <span class="tl-tag">TAG</span>
            <span class="tl-tag">TAG</span>
          </div>
        </div>
      </div>
      <!-- Repeat .tl-event up to ~6 times per timeline -->
    </div>
  </div>
</section>
```

The first six `.tl-event` get cyan / brand / brand-glow / amber / violet / rose dot borders automatically (CSS `:nth-child`). Keep timelines to 6 events or fewer per page.

## Feature grid (two-column "new/fixed", "before/after")

```html
<div class="release-grid">
  <div class="release-col">
    <h3><span class="col-dot" style="background:var(--brand)"></span> COLUMN A LABEL</h3>
    <div class="feat-list">
      <div class="feat-item">
        <h5><span class="feat-icon" style="background:rgba(13,148,136,0.12)">🎮</span> Feature name</h5>
        <p>Description. Inline <span class="feat-code">code</span> via .feat-code.</p>
      </div>
      <!-- More .feat-item -->
    </div>
  </div>
  <div class="release-col">
    <h3><span class="col-dot" style="background:var(--accent-rose)"></span> COLUMN B LABEL</h3>
    <div class="feat-list">
      <!-- More .feat-item -->
    </div>
  </div>
</div>
```

## 3-up highlight grid

```html
<div class="h-grid">
  <div class="h-card">
    <div class="h-icon">📈</div>
    <h4>Title</h4>
    <p>Body text.</p>
    <div class="h-meta">META LABEL</div>
  </div>
  <!-- 3-6 .h-card; nth-child colors the icon backgrounds automatically.
       Metadata goes in .h-meta — NOT .tl-tags/.tl-tag (those belong to .tl-event timeline cards). -->
</div>
```

Each `.h-card p` body should be **2+ sentences with a concrete detail**, not a one-line label. Use `.h-meta` (one short uppercase tag), not `.tl-tags`.

## Impact stats + quotes

```html
<div class="impact-grid">
  <div class="impact-card">
    <div class="impact-val">303</div>
    <div class="impact-label">FIRST METRIC<br>LABEL</div>
  </div>
  <!-- Exactly 4 .impact-card; nth-child colors the value automatically -->
</div>

<div class="impact-quotes" style="margin-top:40px;">
  <div class="impact-quote">
    <p>The quote itself, in italic body type.</p>
    <span class="quote-src">— Attribution</span>
  </div>
  <!-- 2 quotes side by side -->
</div>
```

## Verdict callout (one-line takeaway)

A boxed takeaway with a mono label, a bold answer, and an optional paragraph. Default is green ("yes"); add `.maybe` for amber or `.no` for rose. Use it to land the point at the end of a section.

```html
<div class="verdict">
  <div class="v-label">THE ONE-LINE SUMMARY</div>
  <div class="v-answer">The single sentence a reader should walk away with — <em>italics</em> for the key phrase.</div>
  <p>An optional sentence or two of nuance underneath.</p>
</div>

<div class="verdict maybe">
  <div class="v-label">THE HONEST CAVEAT</div>
  <div class="v-answer">Use <code>.maybe</code> (amber) when the answer is "it depends".</div>
</div>
```

## Step cards + resource links (typical end-of-tab CTA)

```html
<div class="step-grid">
  <div class="step-card">
    <div class="step-num">01</div>
    <h4>Step title</h4>
    <p>What to do.</p>
    <code>shell command or example</code>
  </div>
  <!-- 3 .step-card -->
</div>

<div class="resource-grid">
  <a class="resource-card" href="#" target="_blank" rel="noopener">
    <div class="res-icon">📋</div>
    <h5>Resource name</h5>
    <p>resource.example.com</p>
  </a>
  <!-- EXACTLY 4 .resource-card — the grid is 4 columns; 3 or 5 cards leave a visible gap -->
</div>

<div class="footer-bar">
  <p>DOC TITLE · DATE · MADE WITH MODEL NAME</p>
</div>
```

## Changelog entry (for the deep-dive tab)

```html
<div class="changelog-entry">
  <div class="ce-header">
    <h2 class="ce-title">Entry title</h2>
    <div class="ce-meta">
      <span class="ce-tag date">May 8, 2026</span>
      <span class="ce-tag ver">v0.130.0</span>
      <span class="ce-tag">60 CHANGES</span>
    </div>
  </div>
  <p class="ce-summary">One-paragraph summary.</p>

  <div class="ce-section">
    <h4>Section heading</h4>
    <ul>
      <li>Bullet with <code>code</code> and <strong>emphasis</strong>.</li>
      <li>Another bullet.</li>
    </ul>
  </div>

  <div class="ce-section">
    <h4>Another section</h4>
    <ul>
      <li>...</li>
    </ul>
  </div>
</div>
```

Color the left-rail by adding a modifier class:
- `.changelog-entry.accent-cyan`
- `.changelog-entry.accent-green`
- `.changelog-entry.accent-amber`
- `.changelog-entry.accent-rose`
- `.changelog-entry.accent-violet`

(Default rail is `--brand`.)

## Sources grid (for the sources tab)

```html
<div class="sources-grid">
  <a class="source-card" href="https://example.com" target="_blank" rel="noopener">
    <div class="src-icon">📋</div>
    <h4>Source title</h4>
    <p>Short description of what's at this source.</p>
    <div class="src-url">example.com/path</div>
  </a>
  <!-- More .source-card -->
</div>
```

## Glossary (for the glossary tab)

Plain-English definitions of terms used elsewhere in the doc. Lives inside a `.doc-page` wrapper on `glossary.html`. The simplest form is a flat `.glossary-list`:

```html
<div class="doc-page">
  <div class="doc-hero">
    <h1>Glossary</h1>
    <p>Plain-English definitions for the terms used across this doc.</p>
  </div>

  <div class="glossary-list">
    <div class="glossary-term" id="api">
      <div class="gt-head">
        <h3 class="gt-term">API</h3>
        <span class="gt-tag">ACRONYM</span>
      </div>
      <p class="gt-def">A way for two programs to talk to each other — like a waiter taking your order to the kitchen and bringing food back.</p>
      <div class="gt-seen">Appears in: Overview, Deep-dive</div>
    </div>
    <div class="glossary-term accent-violet" id="webhook">
      <div class="gt-head">
        <h3 class="gt-term">Webhook</h3>
      </div>
      <p class="gt-def">An automatic message one app fires off to another the moment something happens — like a doorbell that rings a <strong>different</strong> house.</p>
    </div>
    <!-- More .glossary-term, one per term -->
  </div>
</div>
```

- `.gt-tag` (optional) labels the kind of term — `ACRONYM`, `TOOL`, `CONCEPT`, etc.
- `.gt-seen` (optional) tells the reader which tabs the term shows up in.
- Give each `.glossary-term` an `id` so the rest of the doc can deep-link to it (`<a href="glossary.html#api">API</a>`).
- The left rail defaults to `--brand`; add `.accent-cyan` / `.accent-green` / `.accent-amber` / `.accent-rose` / `.accent-violet` to vary it.

For a longer glossary, add a jump bar and cluster terms into groups (alphabetical or by category):

```html
<div class="doc-page">
  <div class="doc-hero">
    <h1>Glossary</h1>
    <p>Plain-English definitions for the terms used across this doc.</p>
  </div>

  <div class="glossary-index">
    <a href="#group-a">A</a>
    <a href="#group-b">B</a>
    <a href="#group-models">Model terms</a>
  </div>

  <div class="glossary-group" id="group-a">
    <h2 class="gg-letter">A</h2>
    <div class="glossary-list">
      <div class="glossary-term" id="api"> … </div>
    </div>
  </div>

  <div class="glossary-group" id="group-b">
    <h2 class="gg-letter">B</h2>
    <div class="glossary-list">
      <!-- .glossary-term cards -->
    </div>
  </div>
</div>
```

Pick one ordering scheme (alphabetical *or* category) — don't mix. End the page with `.page-pagination` and a `.footer-bar` like any other secondary tab.

## Prev/next pagination (end of secondary tabs)

```html
<!-- On examples.html, in a doc with tabs: Overview → Cheat Sheet → Examples → Glossary → Sources -->
<div class="page-pagination">
  <a href="cheat-sheet.html">
    <div class="pp-label">← PREVIOUS</div>
    <div class="pp-title">Cheat Sheet</div>
  </a>
  <a href="glossary.html" class="next">
    <div class="pp-label">NEXT →</div>
    <div class="pp-title">Glossary</div>
  </a>
</div>
```

**Follow the tab-bar order exactly.** `← PREVIOUS` is the tab immediately to the **left** of the current page; `NEXT →` is the tab immediately to the **right**. Don't jump `← PREVIOUS` back to `index.html` from a page that isn't second in the order — that skips a tab (a common mistake: the Examples page linking PREVIOUS to Overview instead of Cheat Sheet). The Overview (`index.html`) carries no pagination; the last tab omits the `NEXT` link (the flex layout pushes the remaining one to the correct side). Always keep the arrow glyphs (`← PREVIOUS`, `NEXT →`), and link **only within this doc** — pagination is intra-doc navigation, never a link to a sibling doc.

## Fade-up animation

Add `.fade-up` to any element. Optionally add `.stagger-1` through `.stagger-5` for delay. The `nav-script.js` IntersectionObserver toggles `.visible` when the element enters the viewport.

```html
<h1 class="fade-up">Animates on entry</h1>
<p class="fade-up stagger-1">200ms after the h1</p>
<p class="fade-up stagger-2">300ms after the h1</p>
```

Don't put `.fade-up` on the tab bar, the page-nav dots, or other fixed-position elements — they're already visible at load.
