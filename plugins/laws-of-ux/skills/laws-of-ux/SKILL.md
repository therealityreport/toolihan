---
name: laws-of-ux
description: This skill should be used when auditing or grading a frontend project's UX against the Laws of UX (lawsofux.com) — when the user runs /ux-audit, asks to "grade the UX", "audit usability", "review information architecture / visual hierarchy / forms", wants per-law findings, a 0-100 + A-F grade, or prioritized code-level fixes. Provides the 30-law knowledge base, concrete source-code adherence/violation signals, the applicability + confidence scoring rubric, the concern-area dispatch map, stack detection, and the report/scorecard contract. It is the single source of truth that the /ux-audit command, the ux-auditor and ux-synthesizer subagents, and /ux-explain all read.
---

# Laws of UX — audit knowledge base & grading rubric

This skill is the **single source of truth** for grading a frontend project against the
30 [Laws of UX](https://lawsofux.com) (Jon Yablonski). The `/ux-audit` command, the
`ux-auditor` and `ux-synthesizer` subagents, and the `/ux-explain` command all read from here so
scoring stays consistent across platforms (Claude Code and Codex) and across every pass.

The laws are grouped into four families that mirror the site: **Heuristics**, **Gestalt
Principles**, **Cognitive Biases**, and general **Principles**, plus a set of **newer
additions**. Every law has its own file under `references/laws/` — load only the files for the
concern area you are auditing (see `references/concern-areas.md`).

## The core principle: grade honestly, or don't grade

The hard part of a UX audit is not listing laws — it's **not faking precision**. Only about
a third of the 30 laws are reliably detectable from source; a third need rendered geometry or
runtime numbers; a third aren't statically measurable at all. So this skill makes
**applicability** and **detection-confidence** first-class:

- **Only laws that are APPLICABLE _and_ ASSESSED move the grade.** Everything else is listed
  separately, never averaged in.
- **Every finding must carry `file:line` evidence.** A candidate with no confirmable evidence
  becomes a "needs review" advisory — it never penalizes the grade.
- **The report always states what it could not see** (N/A laws, laws that need `--url`, the
  sampling done on large repos). That disclosure is what makes the grade trustworthy.

Never invent a violation to fill a category. Never emit a grade for a repo with no frontend.

## How the laws are stored

**One file per law** under `references/laws/` (30 files), so an auditor loads only the exact
laws its concern area owns — the tightest possible context. `references/laws/README.md` is the
family-grouped index (Heuristics · Gestalt · Cognitive Biases · Principles · Newer additions),
and `references/concern-areas.md` maps each concern area to the specific per-law files to load.

Every law file uses the **same fixed schema** so auditors parse it uniformly:

```
# <Law name>
**<Family> · weight 1-3 · tier a/b/c · SCORED | ADVISORY**
- Definition / Why it matters
- Applies when:        (the applicability gate — else N/A)
- Adherence signals:   (greppable evidence of compliance)
- Violation signals:   (greppable evidence + how to locate: file globs + patterns)
- Confidence:          a = reliable-static · b = heuristic · c = needs-live-or-visual
- Example fix:         (before/after snippet)
```

## The 30 laws at a glance

`w` = weight (1 nice-to-have · 2 important · 3 critical). `tier` = static-detection confidence
(a reliable · b heuristic · c needs live/visual). `S/A` = SCORED or ADVISORY-only.

| Law | Family | Owner area | w | tier | S/A |
|---|---|---|---|---|---|
| Hick's Law | Heuristic | IA | 3 | b | S |
| Jakob's Law | Heuristic | IA | 2 | b | S |
| Miller's Law | Heuristic | IA | 2 | b | S |
| Serial Position Effect | Bias | IA | 1 | b | S |
| Choice Overload | Newer | IA | 2 | b | S |
| Chunking | Newer | IA | 2 | b | S |
| Working Memory | Newer | IA | 2 | b | S |
| Aesthetic-Usability Effect | Heuristic | Visual | 2 | c | S |
| Law of Similarity | Gestalt | Visual | 2 | a | S |
| Law of Proximity | Gestalt | Visual | 2 | b | S |
| Law of Common Region | Gestalt | Visual | 2 | b | S |
| Law of Uniform Connectedness | Gestalt | Visual | 1 | b | S |
| Law of Prägnanz | Gestalt | Visual | 1 | c | S |
| Von Restorff Effect | Bias | Visual | 2 | a | S |
| Selective Attention | Newer | Visual | 2 | b | S |
| Doherty Threshold | Principle | Interaction | 3 | b | S |
| Fitts's Law | Heuristic | Interaction | 2 | b | S |
| Goal-Gradient Effect | Heuristic | Interaction | 2 | b | S |
| Peak-End Rule | Bias | Interaction | 2 | c | S |
| Zeigarnik Effect | Bias | Interaction | 1 | b | S |
| Flow | Newer | Interaction | 1 | c | S |
| Postel's Law | Principle | Forms | 3 | a | S |
| Tesler's Law | Principle | Forms | 2 | b | S |
| Parkinson's Law | Heuristic | Forms | 1 | c | S |
| Cognitive Load | Newer | Forms | 3 | b | S |
| Occam's Razor | Principle | Forms | 2 | c | S |
| Mental Model | Newer | IA | — | — | A |
| Paradox of the Active User | Newer | Interaction | — | — | A |
| Pareto Principle | Principle | Forms | — | — | A |
| Cognitive Bias | Newer | — | — | — | A |

**25 SCORED laws · 5 ADVISORY.** The advisory five are documented and surfaced as notes but
are **never graded from static source** — they need usage analytics, user research, or are a
category label, not a testable rule. Scoring them would be theater. See
`references/scoring-rubric.md` for why.

## Composite auditing (avoid double-counting)

Several laws measure the same evidence. When scoring, treat these as composites so the same
finding isn't counted three times:

- **Chunking + Miller's + Working Memory** → one "information-chunking & memory-load" judgment.
- **Hick's + Choice Overload** → one "choice-load" judgment.
- **Jakob's** absorbs the measurable part of **Mental Model** (conventions are externalized
  mental models); the rest of Mental Model stays advisory.

`references/concern-areas.md` names the single **owning** concern area for each law so the
roll-up scores it exactly once.

## The four concern areas (how `/ux-audit` fans out)

| Concern area | Laws scored (owner) |
|---|---|
| **Information Architecture & Navigation** | Hick's/Choice-Overload, Miller's/Chunking/Working-Memory, Jakob's, Serial Position |
| **Visual Hierarchy & Gestalt** | Similarity, Proximity, Common Region, Uniform Connectedness, Prägnanz, Von Restorff, Aesthetic-Usability, Selective Attention |
| **Interaction & Feedback** | Doherty, Fitts's, Goal-Gradient, Peak-End, Zeigarnik, Flow |
| **Forms & Input** | Postel's, Tesler's, Parkinson's, Cognitive Load, Occam's Razor |

Each area maps to one dispatch of the `ux-auditor` subagent (Claude) or one sequential pass
(Codex); the `ux-auditor` gathers evidence and scores its owned laws, then the `ux-synthesizer`
subagent rolls all four areas' findings into the final grade and report. Full map +
reference-file loading per area: `references/concern-areas.md`.

## Scoring (summary — full formula in `references/scoring-rubric.md`)

1. Classify each law per surface: **APPLICABLE / NOT_APPLICABLE / NOT_ASSESSED**. Only
   `APPLICABLE + ASSESSED + SCORED` laws enter the grade.
2. Score each such law from evidence on a **0–4 ordinal** → `s ∈ [0,1]`.
3. Weight by importance `w ∈ {1,2,3}` and detection-confidence `c ∈ {1.0, 0.6, 0.3}` (a `--url`
   live measurement bumps the relevant law's `c` to 1.0).
4. `CategoryScore = Σ(w·c·s) / Σ(w·c)`; `Overall = Σ(W_C·CategoryScore) / Σ(W_C)`.
5. Letters: **A ≥ 90 · B 80–89 · C 70–79 · D 60–69 · F < 60**.
6. Always print **one honest grade + a coverage band** — e.g. `B (82) — assessed 19/30 laws
   (5 N/A, 5 advisory-only; run --url to assess 3 more)`. If < 50% of a category's applicable
   laws were assessed, **suppress that category's letter** ("insufficient coverage").

## Report & scorecard contract

- The Markdown report follows `templates/report-template.md` exactly: header, overall grade +
  verdict, category breakdown, findings table (`Law · Severity · file:line · Evidence ·
  Recommendation · Fix`), prioritized fixes (Quick wins then Larger efforts), and a **Coverage
  & limits** section listing N/A + needs-live + advisory laws and any sampling.
- With `--html`, also render `templates/scorecard/scorecard.html` (copy `scorecard.css`
  alongside it): a grade dial, per-category bars, the findings table, the prioritized fix list,
  and the coverage panel. It reuses the shadcn/Geist token system so it matches the
  infographic-docs look, and is self-contained (no external plugin dependency).

## Read-only stance

This skill and the `ux-auditor` never edit files. The `ux-synthesizer` writes **only report
artifacts** (the Markdown report and, with `--html`, the scorecard) — never project source.
Fixes are emitted as **snippets/diffs inside the report**. Only `/ux-fix` edits project files,
and only one finding at a time, dry-run by default, after re-confirming the evidence and getting
explicit approval. Larger-effort/structural fixes are described, not auto-applied.

## Reference files

- `references/laws/` — **one file per law** (30), each with that law's definition, code signals,
  weight, tier, and example fix. Family-grouped index: `references/laws/README.md`.
- `references/scoring-rubric.md` — the exact formula, weights, applicability + confidence, roll-ups, coverage band.
- `references/concern-areas.md` — concern-area → owning-law map + which per-law files each auditor loads.
- `references/stack-detection.md` — per-framework detection, what to scan, design-system crediting, sampling, the no-frontend refusal.
- `references/live-audit.md` — the optional `--url` pass: which chrome-devtools MCP tools measure which laws.

## Templates

- `templates/report-template.md` — the Markdown report skeleton.
- `templates/scorecard/scorecard.html` + `templates/scorecard/scorecard.css` — the HTML scorecard.
