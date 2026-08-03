# Fixture: known-bad

A deliberately flawed plain HTML/CSS/JS app. Used to test the auditor's **recall** — it should
catch these planted violations, each with real `file:line` evidence.

## Planted violations (expected findings)

| Law | Where | Signal |
|---|---|---|
| Hick's Law | `index.html` nav | 14 flat, ungrouped top-level nav items |
| Fitts's Law | `styles.css` `.icon-btn` | 24×24 icon button, no padding (below ~44px floor) |
| Von Restorff / Similarity | `index.html` `.cta-row`, `styles.css` `.btn-primary` | two competing "primary" buttons; no visual emphasis on the true primary |
| Miller's / Chunking | `index.html` `#signup` | 9 ungrouped inputs, no `<fieldset>` sections |
| Common Region / Proximity | `styles.css` `#signup` | no grouping container; uniform spacing ignores relationships |
| Postel's Law | `app.js` `STRICT_EMAIL` | over-strict email regex; no `trim()`/normalization; no `autocomplete` |
| Doherty Threshold | `app.js` submit handler | `await fetch` with no loading/pending UI, no optimistic update |
| Parkinson's / Tesler's | `index.html` form | no `autocomplete`, no defaults |

Expected outcome: a low-ish grade (D/F range in the assessed categories) with these findings
surfaced, all backed by `file:line`. This is a static-only fixture (no `--url`), so
Aesthetic-Usability / Prägnanz / Peak-End should be reported as **NOT_ASSESSED**, not graded.
