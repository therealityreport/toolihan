# Goal-Gradient Effect

**Heuristic · weight 2 · tier b · SCORED · owner: Interaction**

- **Definition / why it matters:** Motivation to finish increases with proximity to the goal.
  Multi-step flows without visible progress feel endless.
- **Applies when:** there is a multi-step flow — checkout, onboarding, a wizard, a long form
  split into steps, a signup funnel.
- **Adherence signals:** a progress indicator — `<progress>`, a stepper/`Stepper`, "Step 2 of
  4" text, a progress bar, endowed-progress patterns (starting partway).
- **Violation signals:** a multi-step flow (grep `step`, `wizard`, `onboarding`, `checkout`,
  routed sub-steps) with **no** progress affordance.
- **Confidence:** b — you can detect "steps exist but no progress UI"; whether the gradient
  *motivates* is behavioral.
- **Example fix:** add a step indicator ("Step 2 of 4") or a `<progress>` bar to the wizard.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
