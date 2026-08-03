# Jakob's Law

**Heuristic · weight 2 · tier b · SCORED · owner: IA**

- **Definition / why it matters:** Users spend most of their time on other sites and expect
  yours to work the same way. Reinvented conventions raise the learning cost.
- **Applies when:** the project has a site/app shell — header, nav, forms, or standard
  controls. Else N/A.
- **Adherence signals:** semantic landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`); logo
  in the header linking to `/`; conventional placement (primary nav top/left, account/cart
  top-right, search with a magnifier); labels above inputs; submit on the right of cancel.
- **Violation signals:** custom controls where a native one exists (`<div onClick>` acting as a
  button with no `role`/`tabindex`); links styled as buttons and vice-versa; no landmark
  elements (`grep -L '<main'`); nonstandard placement of core affordances. Absorbs the
  measurable part of **Mental Model**.
- **Confidence:** b — "conventional for your category" needs product knowledge; report
  convention *coverage*, not correctness of a deliberate deviation.
- **Example fix:** replace `<div onClick>` navigation with `<button>`/`<a>`; add `<main>`,
  `<nav aria-label>` landmarks; move the submit button to the conventional position.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
