# Parkinson's Law

**Heuristic · weight 1 · tier c · SCORED · owner: Forms**

- **Definition / why it matters:** Work expands to fill the time available; reduce perceived
  time/effort and users finish faster.
- **Applies when:** there are task flows or forms the user must complete.
- **Adherence signals (weak, static):** autofill (`autocomplete` attributes), smart defaults
  pre-filled, "skip" affordances, async/non-blocking validation.
- **Violation signals (static proxy):** forms with no `autocomplete`, no defaults, blocking
  submit-only validation.
- **Confidence:** **c** — this is really about task-completion *time*; mostly needs the runtime
  path. Score conservatively from the autofill/defaults proxy or mark NOT_ASSESSED.
- **Example fix:** add `autocomplete` tokens, sensible defaults, and inline (non-blocking) validation.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
