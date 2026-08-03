# Community 30 Days templates

Copy these files into a generated report folder, then replace every `{{PLACEHOLDER}}`.

Required shared assets:

- Copy `skills/infographic-doc/assets/styles.css` to `assets/styles.css`.
- Copy `skills/infographic-doc/templates/nav-script.js` to `assets/nav-script.js`.

Default tab order:

1. `index.html`
2. `signal-map.html`
3. `source-detail.html`
4. `github.html`
5. `glossary.html`
6. `sources.html`

Omit `github.html` only when GitHub is genuinely irrelevant. If omitted, remove the GitHub tab link from every template page and update prev/next links.

Placeholder groups:

- `{{DOC_TITLE}}` - readable title, such as "Codex Plugins Community Pulse".
- `{{DOC_MARK}}` - two-letter mark, such as "CP".
- `{{DATE_WINDOW}}` - exact range, such as "2026-05-23 to 2026-06-22".
- `{{MODEL_NAME}}` - model/runtime that produced the doc.
- `{{TOPIC}}` - researched topic.
- `{{VERDICT}}` - one-sentence practical takeaway.
- `{{SOURCE_LIMITS}}` - source limits, or "No major source limits."

Do not leave placeholders in final output. Run `rg '{{' <doc-folder>` before final response.
