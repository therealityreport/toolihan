# Law of Proximity

**Gestalt · weight 2 · tier b · SCORED · owner: Visual**

- **Definition / why it matters:** Objects near each other are perceived as a group. Spacing
  that doesn't reflect relationships makes layouts read wrong.
- **Applies when:** the UI groups related content or has labeled controls.
- **Adherence signals:** tighter spacing within a group than between groups (`gap`,
  `space-y-*`, margin patterns that vary by relationship); labels adjacent to their inputs;
  related controls in a shared container.
- **Violation signals:** uniform spacing everywhere with no grouping; a label far from its
  input (separated by unrelated markup); equal margins between related and unrelated items.
- **Confidence:** b — true proximity is visual; static reads the spacing intent.
- **Example fix:** reduce intra-group `gap`, increase inter-group spacing; move each label next
  to its field.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Gestalt Principles). Scoring: `references/scoring-rubric.md`._
