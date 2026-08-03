# Postel's Law (Robustness Principle)

**Principle · weight 3 · tier a · SCORED · owner: Forms**

- **Definition / why it matters:** Be liberal in what you accept, conservative in what you
  send. Forgiving inputs prevent needless rejection and frustration.
- **Applies when:** the project has forms/inputs or accepts user-entered data.
- **Adherence signals:** input normalization — `.trim()`, `.toLowerCase()`, case-insensitive
  compares; flexible parsing of phone/date/card (strip spaces/dashes); lenient, well-known
  validation (`type="email"`, permissive phone); paste handling for codes/cards;
  `autocomplete`/`inputmode` present.
- **Violation signals:** over-strict validation on well-known-forgiving fields — regexes that
  reject `+`, spaces, or dashes in phone; email regexes that reject valid addresses; requiring
  an exact case/format; no `trim()` so trailing spaces fail. Grep validation schemas (`zod`,
  `yup`, `yup.string().matches`, `pattern=`, inline `RegExp`).
- **Confidence:** **a** — genuinely grep-able and high-value. Only flag strictness on fields
  with forgiving norms (email/phone/name/date), **not** arbitrary formats (a coupon code may be
  strict on purpose).
- **Example fix:** `value.trim().toLowerCase()` before compare; accept `+1 (555) 123-4567` by
  stripping non-digits; loosen the email regex to a sane one; add `autocomplete`.

---
_Part of the [Laws of UX](https://lawsofux.com) audit knowledge base (Principles). Scoring: `references/scoring-rubric.md`._
