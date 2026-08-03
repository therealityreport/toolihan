# Peak-End Rule

**Bias · weight 2 · tier c · SCORED · owner: Interaction**

- **Definition / why it matters:** People judge an experience by its most intense point (the
  peak) and its end, more than the average. Success moments and graceful endings dominate
  memory.
- **Applies when:** there are complete journeys — signup, checkout, submission, first-run.
- **Adherence signals (partial, static):** presence of success/confirmation states, empty
  states, graceful error recovery, celebratory/confirmation screens, thoughtful final steps
  (grep `success`, `Confirmation`, `EmptyState`, `error boundary`, `toast`).
- **Violation signals (partial):** async submits with no success feedback; flows that end
  abruptly; missing error/empty states.
- **Confidence:** **c** — the emotional "peak" is behavioral. You can report presence/absence
  of key states as a proxy, but mark the peak judgment NOT_ASSESSED without `--url`/journey
  walking.
- **Example fix:** add a clear success/confirmation state at the end of the flow; design the
  empty and error states, not just the happy path.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Cognitive Biases). Scoring: `references/scoring-rubric.md`._
