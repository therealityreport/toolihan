# Scoring rubric

This is the exact, reproducible grading formula. Its job is to produce a grade that is
**honest about what it could and could not measure**. Follow it literally.

## Step 1 — classify every law (applicability)

Before scoring, put each law (per audited surface) into one of three states:

- **APPLICABLE** — the law's "Applies when" gate is met (there are forms → Postel's applies).
- **NOT_APPLICABLE (N/A)** — no relevant surface exists (no async work → Doherty is N/A; no
  forms → Postel's is N/A). **Excluded from both the numerator and the denominator.** Listed
  separately with the reason. This is what stops a static-content or backend-light repo from
  being punished for laws it cannot exhibit.
- **NOT_ASSESSED** — applicable but not measurable on this run (Aesthetic-Usability with no
  `--url`; a `tier c` law with no live pass). **Excluded from the grade.** Listed under "needs
  live/visual review."

Only laws that are **SCORED (not ADVISORY) + APPLICABLE + ASSESSED** enter the grade. The five
ADVISORY laws (Pareto, Mental Model, Paradox of the Active User, Cognitive Bias — and any law
left NOT_ASSESSED) are reported as notes, never averaged in.

## Step 2 — score each scored law (0–4 ordinal → s)

Assign an ordinal from the evidence, then map to a compliance score `s`:

| Ordinal | Meaning | s |
|---|---|---|
| 4 | Strong adherence, no violations found | 1.00 |
| 3 | Mostly adheres; minor, isolated issues | 0.80 |
| 2 | Mixed; clear violations alongside compliance | 0.55 |
| 1 | Predominantly violated | 0.25 |
| 0 | Severe / systemic violation | 0.00 |

If a check has discrete sub-checks (e.g. Postel's: trims? lenient phone? lenient email? paste?
autocomplete?), you may compute `s = passed / total` directly and map back to the nearest
ordinal for display. When there is genuinely no signal either way, score **3** and say so
rather than guessing low.

## Step 3 — weights and confidence

- **Weight `w ∈ {1, 2, 3}`** — the law's importance to usability (from its reference block).
- **Confidence `c`** — how reliably it was detected, from the law's tier:
  - tier **a** (reliable-static) → `c = 1.0`
  - tier **b** (heuristic) → `c = 0.6`
  - tier **c** (needs live/visual) → `c = 0.3`
  - **A `--url` live measurement bumps that law's `c` to 1.0** (real numbers beat inference).

Confidence-weighting means a weakly-detected law can only nudge the grade, while a rigorously
measured one (Postel's statically, Doherty live) moves it a lot.

## Step 4 — roll up

```
CategoryScore(C) = Σ(wᵢ · cᵢ · sᵢ) / Σ(wᵢ · cᵢ)      # over SCORED+APPLICABLE+ASSESSED laws in C
CategoryPercent  = round(100 · CategoryScore)

Overall = Σ_C (W_C · CategoryScore(C)) / Σ_C (W_C)    # only categories with ≥1 assessed law
OverallPercent = round(100 · Overall)
```

Default **category weights `W_C`** (documented, tunable — the single opinionated knob):

| Category | W_C |
|---|---|
| Heuristics | 1.3 |
| Principles | 1.1 |
| Gestalt | 1.0 |
| Newer additions | 1.0 |
| Cognitive Biases | 0.9 |

A category with zero applicable+assessed laws is dropped from the overall roll-up entirely.

## Step 5 — letter grade + coverage band

```
Letter:  A ≥ 90 · B 80–89 · C 70–79 · D 60–69 · F < 60
```

Always print **one honest grade plus a visible coverage band** — never a second, guessed-at
"full grade" that includes unmeasured laws. Example:

> **B (82)** — assessed 19/30 laws (5 N/A, 5 advisory-only, 1 needs live review; run `--url` to
> assess 3 more).

**Category-letter suppression:** if fewer than **50%** of a category's *applicable* laws were
assessed, do not print that category's letter — show "insufficient coverage (n/m assessed)"
instead of a misleading grade.

Every law line item shows: **state · ordinal/score · confidence · file:line evidence**, so the
grade is auditable by the reader.

## Step 6 — two-stage findings (no false positives in the grade)

Every heuristic first produces a **candidate finding**. Before it counts, the auditor must
re-open the file, read the surrounding render tree, check for library/framework provision
(e.g. a `<Suspense>` boundary higher up, a design-system primitive), and either:

- **confirm** it with concrete `file:line` evidence → it becomes a scored finding; or
- **fail to confirm** → it becomes a **"needs review" advisory**, which **does not** move the
  grade.

**No finding without `file:line` evidence may ever penalize the score.**

## Step 7 — severity & fix effort (for the report)

Per-finding **severity** from `law_weight × violation_ordinal`:

| Condition | Severity |
|---|---|
| weight 3 & ordinal ≤ 1 | Critical |
| weight 3 & ordinal 2, or weight 2 & ordinal ≤ 1 | High |
| weight 2 & ordinal 2, or weight 1 & ordinal ≤ 1 | Medium |
| ordinal 3 (minor) | Low |
| ordinal 4 | Info (note only) |

Each fix is tagged **effort**: `quick-win` (≤ 2 files / ~≤ 15 lines / no new dependency) vs
`larger-effort` (structural / IA / routing changes). The report's fix list sorts by
`severity desc, then effort asc`, surfacing high-severity quick wins first — an explicit
application of the **Pareto Principle** (the ~20% of fixes recovering ~80% of the grade) and
**Occam's Razor** (smallest sufficient change). Say so in the report.

## Optional project overrides

If the target repo contains a `.lawsofux.json`, read it to override defaults (per-law weights,
category weights `W_C`, letter-band thresholds, or a sampling cap). Absent that file, use the
defaults above. Never fail if it's missing or malformed — fall back to defaults and note it.
