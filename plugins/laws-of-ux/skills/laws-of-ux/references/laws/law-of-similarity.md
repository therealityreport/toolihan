# Law of Similarity

**Gestalt · weight 2 · tier a · SCORED · owner: Visual**

- **Definition / why it matters:** Elements that look alike are perceived as related. When
  same-purpose elements are styled inconsistently, users can't tell what goes together.
- **Applies when:** the UI has repeated element types (buttons, links, cards, badges).
- **Adherence signals:** one consistent variant/class per role — every primary button uses the
  same `<Button variant="...">`/class; links are consistently distinguishable from text;
  cards share one component.
- **Violation signals:** the same action styled differently across files (grep button/link
  class strings and compare); ad-hoc `style={{}}` on elements that a shared component covers;
  raw hex `#[0-9a-fA-F]{3,6}` and arbitrary Tailwind `[...]` values instead of tokens.
- **Confidence:** **a** — inconsistency is genuinely grep-detectable and high-value.
- **Example fix:** replace one-off styled buttons with the shared `<Button>` variant; move
  colors to tokens so like elements render alike.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Gestalt Principles). Scoring: `references/scoring-rubric.md`._
