# Zeigarnik Effect

**Bias · weight 1 · tier b · SCORED · owner: Interaction**

- **Definition / why it matters:** People remember incomplete/interrupted tasks better than
  completed ones — surface unfinished work and users come back to finish it.
- **Applies when:** there are multi-step flows, resumable tasks, or profile/setup completion.
- **Adherence signals:** progress saving / draft state; "resume where you left off"; a
  completion checklist ("complete your profile"); badges/notifications for pending items;
  multi-step forms that persist state.
- **Violation signals:** a multi-step flow with **no** state persistence (lose progress on
  reload); no surfacing of incomplete tasks. Grep `draft`, `resume`, `localStorage`,
  `persist`, `autosave`, `progress`.
- **Confidence:** b.
- **Example fix:** persist wizard state to storage and show a "resume" affordance; add a
  profile-completion checklist.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Cognitive Biases). Scoring: `references/scoring-rubric.md`._
