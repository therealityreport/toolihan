<!--
report-template.md — the Markdown report the /ux-audit synthesizer fills.
Replace <placeholders>. Keep every section. Drop a table row only when a section
genuinely has no items, and say so ("None found."). Never omit the Coverage & limits
section — it is what makes the grade honest.
-->

# UX Audit — Laws of UX

**Target:** `<path or URL>` · **Stack:** `<detected stack>` · **Mode:** `<static | static + live (--url)>`
**Files scanned:** `<n>` (`<sampling note, if any>`) · **Date:** `<YYYY-MM-DD>` · **By:** `<model>`

## Overall grade: `<letter>` (`<percent>`/100)

`<one-line verdict — the single most important thing to fix or the standout strength>`

> **Coverage:** assessed `<x>`/30 laws (`<a>` N/A, `<b>` advisory-only, `<c>` need live review).
> `<"Run with --url to assess N more." when static-only and tier-c laws remain.>`

## Category breakdown

| Category | Grade | Score | Assessed / Applicable | N/A |
|---|---|---|---|---|
| Information Architecture & Nav | `<A–F or "insufficient coverage">` | `<0–100>` | `<a/b>` | `<laws>` |
| Visual Hierarchy & Gestalt | | | | |
| Interaction & Feedback | | | | |
| Forms & Input | | | | |

<!-- Suppress a category letter (show "insufficient coverage (n/m)") when <50% of its applicable laws were assessed. -->

## Findings

Most severe first. Every row must have real `file:line` evidence; unconfirmable candidates go
under "Needs review" below, not here.

| Law | Cat | Severity | Basis | Location | Evidence | Recommendation | Suggested fix |
|---|---|---|---|---|---|---|---|
| `<Hick's Law>` | IA | High | static | `<src/components/Nav.tsx:18>` | `<12 flat top-level nav items>` | `<Group into ≤5 sections + overflow>` | `<see fix #1>` |

## Prioritized fixes

Sorted severity-first, then smallest effort — the ~20% of changes that recover most of the
grade (Pareto), each the smallest sufficient change (Occam).

### Quick wins (high impact, low effort)
1. **[`<severity>`] `<Law>`** — `<file:line>` — `<what & why>`. _`<~n lines>`_
   ```diff
   - <before>
   + <after>
   ```

### Larger efforts (structural)
1. **[`<severity>`] `<Law>`** — `<area>` — `<described change; not an auto-diff>`. _`<multi-file>`_

## Coverage & limits

- **Not applicable** (excluded from grade): `<law — reason>`, …
- **Needs live/visual review** (`NOT_ASSESSED` — run `--url`): `<law — why>`, …
- **Advisory (not scored):** Pareto (needs usage analytics), Mental Model (needs user research;
  conventions scored under Jakob's), Paradox of the Active User, Cognitive Bias (category, not a
  rule). `<any concrete advisory notes>`
- **Sampling:** `<what was sampled and why, if a large repo>`
- **Method:** confidence-weighted mean over applicable+assessed laws; N/A and unmeasured laws
  excluded; every finding backed by file:line. Weights & formula: `references/scoring-rubric.md`.

## Needs review (unconfirmed candidates — did not affect the grade)
- `<candidate — why it could not be confirmed statically>`

---
_Next: `/ux-fix <finding>` to apply a specific fix (dry-run first) · `/ux-explain <law>` to learn more._
