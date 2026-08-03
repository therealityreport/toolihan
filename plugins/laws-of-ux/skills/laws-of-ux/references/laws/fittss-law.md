# Fitts's Law

**Heuristic · weight 2 · tier b · SCORED · owner: Interaction**

- **Definition / why it matters:** Time to acquire a target is a function of its distance and
  size. Tiny or crowded targets are slow and error-prone, especially on touch.
- **Applies when:** the UI has interactive targets (`<button>`, `<a>`, `[role=button]`, icon
  buttons, form controls).
- **Adherence signals:** touch targets ≥ ~44×44 (iOS) / 48×48 (Material) — `min-h-11`/`min-w-11`,
  `p-3`+, explicit `min-height`; large, prominent primary CTAs; spacing between adjacent
  destructive and safe actions.
- **Violation signals:** interactive targets below floor — Tailwind `h-6`/`h-7`/`w-6`,
  `p-0.5`/`p-1`, inline `height:24px`/`width:24px`; **icon-only** `<button>` with only an
  `<svg>`/icon and no padding or explicit size; a destructive action placed hard against a safe
  one. Locate CSS/utility classes on `button`, `a`, `[role=button]`.
- **Confidence:** b — computed size depends on the cascade, `em` units, and flex-stretch, so a
  button with no explicit height can still render fine. **Flag as "verify", never a hard fail
  from static CSS.** The `--url` pass measures real hit areas with `getBoundingClientRect`.
- **Example fix:** `class="p-0.5"` → `class="p-3 min-h-11 min-w-11"`; add spacing/`gap` between
  Delete and Save.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Heuristics). Scoring: `references/scoring-rubric.md`._
