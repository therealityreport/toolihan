# Law of Common Region

**Gestalt · weight 2 · tier b · SCORED · owner: Visual**

- **Definition / why it matters:** Elements inside a shared, clearly bounded area are perceived
  as a group. Boundaries (cards, panels, fieldsets) create instant structure.
- **Applies when:** the UI has related content that should read as a unit.
- **Adherence signals:** grouping containers — `<Card>`/`.card`, bordered/`bg-*` panels,
  `<fieldset>` around related fields, sections with a boundary.
- **Violation signals:** related fields/items not enclosed in any shared region; long forms
  with no sectioning containers; content that relies only on whitespace where a boundary is
  warranted.
- **Confidence:** b — presence of grouping containers is reasonably grep-able.
- **Example fix:** wrap a related field cluster in `<fieldset>`/`<Card>`; give a settings group
  its own bordered panel.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Gestalt Principles). Scoring: `references/scoring-rubric.md`._
