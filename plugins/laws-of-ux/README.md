# laws-of-ux

Audit and grade a frontend project against the **30 [Laws of UX](https://lawsofux.com)** — and
get prioritized, code-level fixes back. It detects your UI stack, scores each *applicable* law
from concrete source-code signals, and produces a graded report plus an optional HTML scorecard.

Dual-platform (Claude Code + Codex). Read-only by default.

## What makes it trustworthy

Most "UX scores" fake precision. This one doesn't. Only about a third of the 30 laws are
reliably detectable from source; a third need a running app; a third need human/visual judgment.
So the plugin makes **applicability** and **detection-confidence** first-class:

- Only laws it can actually assess move the grade. N/A and unmeasurable laws are excluded and
  **listed**, never averaged in.
- Every finding carries `file:line` evidence — unconfirmable ones become advisories, not
  penalties.
- Every report ends with a **Coverage & limits** section stating what it could not see.
- It **refuses to grade a repo with no frontend** rather than inventing a number.

## Install

```
/plugin marketplace add therealityreport/toolihan
/plugin install laws-of-ux@toolihan
```

## Commands

| Command | What it does |
|---|---|
| `/ux-audit [path] [--url <addr>] [--html] [--out <file>] [--area ia\|visual\|interaction\|forms\|all] [--quick]` | Detect the stack, audit each concern area, print a graded report (0-100 + A-F) with a findings table and prioritized fixes. |
| `/ux-fix <finding \| law \| file:line> [--apply]` | Apply one fix from a prior report. Dry-run by default; edits only after `--apply` + confirmation. |
| `/ux-explain <law>` | Explain one law, its source-code signals, and an example fix. |

### Static by default, live on demand
`/ux-audit ./app` reads source and works fully offline. Add `--url http://localhost:3000` to
also run a live pass with the `chrome-devtools` MCP — real Lighthouse/Core-Web-Vitals numbers
for **Doherty**, real tap-target geometry for **Fitts's**, and rendered screenshots for the
visual/aesthetic laws that static analysis can't judge honestly. `--html` additionally renders a
scorecard in the shadcn/Geist visual style.

## How grading works

1. Each law is classified **APPLICABLE / N/A / NOT_ASSESSED**; only applicable + assessed +
   scored laws count.
2. Each is scored 0–4 from evidence, weighted by importance `w` and detection-confidence `c`
   (a `--url` measurement raises confidence to full).
3. `CategoryScore = Σ(w·c·s)/Σ(w·c)`; overall is the category-weighted mean; letters are
   **A ≥ 90 · B 80–89 · C 70–79 · D 60–69 · F < 60**.
4. The grade prints with a coverage band, e.g. `B (82) — assessed 19/30 laws (5 N/A, 5 advisory;
   run --url to assess 3 more)`. Full formula: `skills/laws-of-ux/references/scoring-rubric.md`.

## The 30 laws & 4 concern areas

| Concern area | Laws scored |
|---|---|
| Information Architecture & Nav | Hick's, Jakob's, Miller's, Serial Position, Choice Overload, Chunking, Working Memory |
| Visual Hierarchy & Gestalt | Similarity, Proximity, Common Region, Uniform Connectedness, Prägnanz, Von Restorff, Aesthetic-Usability, Selective Attention |
| Interaction & Feedback | Doherty, Fitts's, Goal-Gradient, Peak-End, Zeigarnik, Flow |
| Forms & Input | Postel's, Tesler's, Parkinson's, Cognitive Load, Occam's Razor |

Advisory (documented, never scored — they need usage analytics or user research): Pareto,
Mental Model, Paradox of the Active User, Cognitive Bias.

## Supported stacks

React/Next, Vue/Nuxt, Svelte/SvelteKit, Angular, Astro, Solid, plain HTML/CSS, Tailwind, and
CSS-in-JS. Component-library primitives (shadcn/Radix/MUI/Chakra) are **credited** where they
satisfy a law; composition is still audited. Large repos are sampled (and the report says so).

## Safety

Read-only by default — `/ux-audit` and the `ux-auditor` subagent never edit your code; fixes are
emitted as snippets/diffs. `/ux-fix` is the only path that edits: one finding at a time, dry-run
by default, and only after re-confirming the evidence and getting explicit approval.

## Verify it

```
node --test tests/validate-plugin.mjs        # structural contract
/ux-audit tests/fixtures/known-bad           # recall: catches planted issues
/ux-audit tests/fixtures/known-good          # precision: few/no false positives
/ux-audit tests/fixtures/no-frontend         # refusal: no grade emitted
```

## Attribution

The Laws of UX are catalogued by **Jon Yablonski** at [lawsofux.com](https://lawsofux.com). This
plugin's reference files are **original summaries describing source-code signals** for auditing —
not copies of the law texts. Please support the original project and book.

MIT licensed. A local Claude Code / Codex plugin.
