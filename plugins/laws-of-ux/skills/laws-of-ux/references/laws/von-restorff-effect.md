# Von Restorff Effect (Isolation Effect)

**Bias · weight 2 · tier a · SCORED · owner: Visual**

- **Definition / why it matters:** When many similar items are present, the one that differs is
  most remembered. The primary action must stand out; if everything shouts, nothing does.
- **Applies when:** a view has multiple actions/buttons or a set of comparable items.
- **Adherence signals:** exactly **one** visually distinct primary action per view — one
  `variant="primary"`/`variant="default"`/filled button, with secondary actions styled as
  outline/ghost/link.
- **Violation signals:** **multiple competing** primary/filled CTAs in the same render tree
  (grep `variant="primary"`, `variant="default"`, `.btn-primary`, filled-button classes and
  count per view); or a primary CTA styled identically to secondary actions (no emphasis at
  all). Scope strictly to one screen/route — two "primary" buttons in different views don't
  compete.
- **Confidence:** **a** — a visual-emphasis-conflict detector is fairly reliable statically.
- **Example fix:** demote extra primaries to `variant="outline"`/`ghost`; leave one filled CTA;
  or promote the true primary if none stands out.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Cognitive Biases). Scoring: `references/scoring-rubric.md`._
