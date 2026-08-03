# Fixture: known-good

A deliberately correct plain HTML/CSS/JS app. Used to test the auditor's **precision** — it
should produce few/no false positives here, and credit the adherence signals.

## Adherence signals present

| Law | Where | Signal |
|---|---|---|
| Hick's / Jakob's | `index.html` nav | 5 grouped items + `<details>` overflow; semantic landmarks |
| Fitts's Law | `styles.css` `.btn`, inputs | ≥44px min-height targets |
| Von Restorff / Similarity | `.cta-row` | exactly one filled primary; secondary is outline |
| Common Region / Chunking | `#signup` | `<fieldset>`/`<legend>` groups; related fields together |
| Postel's Law | `app.js` `normalizeEmail`/`isEmail` | `trim().toLowerCase()`; permissive email check; `autocomplete`/`inputmode` |
| Doherty Threshold | `app.js` submit | disabled + "Creating…" loading state around `await` |
| Peak-End Rule | `app.js` | explicit success + graceful error messages |

Expected outcome: a high grade in the assessed categories with no fabricated violations. As with
known-bad, the tier-c laws (Aesthetic-Usability, Prägnanz) are **NOT_ASSESSED** without `--url`.
