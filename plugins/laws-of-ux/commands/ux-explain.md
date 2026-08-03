---
description: Explain one Law of UX — its definition, why it matters, the concrete source-code signals that indicate adherence vs violation, and an example fix. A teaching helper; makes no changes.
argument-hint: "<law-name>"
---

Explain a single Law of UX. Requested law: `$ARGUMENTS`.

Look the law up in the `laws-of-ux` skill's per-law files under `references/laws/` (one file per
law; the family-grouped index is `references/laws/README.md`). Match loosely on name (e.g.
"hicks" → `hicks-law.md`, "fitts" → `fittss-law.md`, "doherty" → `doherty-threshold.md`,
"postel" → `postels-law.md`, "von restorff" → `von-restorff-effect.md`). If no law matches, list
the 30 law names from the index grouped by family and ask which one.

Present, in plain language:
1. **Law** (and its family + whether it's SCORED or ADVISORY in the audit).
2. **Definition & why it matters.**
3. **What good looks like** — the adherence signals, with a concrete UI example.
4. **What a violation looks like** — the violation signals and how the auditor detects them
   (the greppable patterns / file globs), plus the confidence tier and what that means
   (reliable-static / heuristic / needs-live-or-visual).
5. **Example fix** — the before/after snippet from the reference.
6. If the law is ADVISORY or tier `c`, explain honestly why static analysis can't fully grade it
   and what would (usage analytics, user research, or a `--url` live pass).

Pure teaching — do not modify any files.
