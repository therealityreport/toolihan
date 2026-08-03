# Hick's Law

**Heuristic · weight 3 · tier b · SCORED · owner: IA**

- **Definition / why it matters:** The time to make a decision grows with the number and
  complexity of choices. Overloaded menus and screens stall and fatigue users.
- **Applies when:** the project renders any nav, menu, toolbar, tab set, `<select>`, filter
  bar, or a screen with multiple simultaneous primary actions. Else N/A.
- **Adherence signals:** grouped/sectioned menus; progressive disclosure (`<details>`,
  accordion, "More"/overflow menus); ≤ ~7 items per group; a clear single primary path.
- **Violation signals:** a single `<nav>`/menu/`role="menubar"` with **> 7 direct interactive
  children**; a `<select>` with a very long ungrouped option list (grep `<option` counts per
  `<select>`, but **whitelist** structured lists — country/state/timezone/currency); flat
  top-level routing with many ungrouped routes (`app/*/page.*`, `pages/*`, `<Route>`,
  `routes` config); many competing CTAs in one view. Locate: `**/*.{tsx,jsx,vue,svelte,html}`
  around `nav`, `menu`, `Menu`, `NavItem`, `<select`.
- **Confidence:** b — count ≠ overload; a long "country" select is fine. Report thresholds
  with context, never a raw count as a failure.
- **Example fix:** group 12 flat nav links into ≤ 5 sections + an overflow menu; move rarely
  used routes under a "More" grouping.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
