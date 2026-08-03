# Aesthetic-Usability Effect

**Heuristic · weight 2 · tier c · SCORED · owner: Visual**

- **Definition / why it matters:** Users perceive aesthetically pleasing design as more usable
  and forgive minor issues. Polish buys goodwill.
- **Applies when:** the project renders a visual UI.
- **Adherence signals (weak, static):** a design-token/theme system present (`tailwind.config`,
  CSS custom properties, a theme file) rather than scattered magic values; consistent spacing
  scale; a component library in use.
- **Violation signals (static proxy only):** heavy ad-hoc `style={{}}`, many raw hex colors,
  arbitrary Tailwind `[...]` values, no shared tokens.
- **Confidence:** **c** — genuine aesthetic judgment needs rendered pixels. Without `--url`,
  mark **NOT_ASSESSED** ("needs visual review") rather than guessing; do **not** infer "uses a
  design system ⇒ pretty". With `--url`, judge from `take_screenshot` at desktop + mobile.
- **Example fix:** consolidate one-off inline styles into design tokens; establish a type/spacing scale.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
