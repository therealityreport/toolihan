# Concern areas → owning laws

`/ux-audit` fans out one `ux-auditor` pass per concern area, then the `ux-synthesizer` rolls the
findings into the graded report. Each law has exactly **one owning area** so the roll-up scores
it once (composites are resolved within the owning area). Each auditor loads only the per-law
files it owns from `references/laws/` — the tightest possible context.

## Information Architecture & Navigation  (`--area ia`)
- **Owns:** Hick's + Choice Overload (composite "choice-load"), Miller's + Chunking + Working
  Memory (composite "chunking & memory-load"), Jakob's (absorbs measurable Mental Model), Serial
  Position.
- **Advisory here:** Mental Model.
- **Scan:** nav/menu components, routing (`app/`, `pages/`, `src/routes`, router config),
  headers/footers, tab sets, `<select>`/filter controls, sidebars.
- **Load:** `references/laws/hicks-law.md`, `choice-overload.md`, `millers-law.md`,
  `chunking.md`, `working-memory.md`, `jakobs-law.md`, `serial-position-effect.md`,
  `mental-model.md`.

## Visual Hierarchy & Gestalt  (`--area visual`)
- **Owns:** Similarity, Proximity, Common Region, Uniform Connectedness, Prägnanz, Von Restorff,
  Aesthetic-Usability, Selective Attention.
- **Scan:** design tokens / theme (`tailwind.config`, CSS custom properties, theme files),
  component styling, button/link variants, cards/panels/fieldsets, layout & spacing, ad-like
  regions.
- **Load:** `references/laws/law-of-similarity.md`, `law-of-proximity.md`,
  `law-of-common-region.md`, `law-of-uniform-connectedness.md`, `law-of-pragnanz.md`,
  `von-restorff-effect.md`, `aesthetic-usability-effect.md`, `selective-attention.md`.

## Interaction & Feedback  (`--area interaction`)
- **Owns:** Doherty Threshold, Fitts's Law, Goal-Gradient Effect, Peak-End Rule, Zeigarnik
  Effect, Flow.
- **Advisory here:** Paradox of the Active User.
- **Scan:** async/data code (`fetch`, `useQuery`/`useMutation`, `await` handlers), loading /
  skeleton / optimistic states, multi-step flows (checkout/onboarding/wizards), success/empty/
  error states, buttons & tap targets, modals/interruptions.
- **Load:** `references/laws/doherty-threshold.md`, `fittss-law.md`, `goal-gradient-effect.md`,
  `peak-end-rule.md`, `zeigarnik-effect.md`, `flow.md`, `paradox-of-the-active-user.md`.

## Forms & Input  (`--area forms`)
- **Owns:** Postel's Law, Tesler's Law, Parkinson's Law, Cognitive Load, Occam's Razor.
- **Advisory here:** Pareto Principle.
- **Scan:** `<form>`/`<input>`/`<select>`/`<textarea>`, validation schemas (`zod`/`yup`/inline
  regex/`pattern=`), `autocomplete`/`inputmode`, defaults/`required` density, field grouping.
- **Load:** `references/laws/postels-law.md`, `teslers-law.md`, `parkinsons-law.md`,
  `cognitive-load.md`, `occams-razor.md`, `pareto-principle.md`.

## `--area all` (default)
Run all four passes, then the synthesizer. `--quick` runs a single combined pass without
subagent fan-out (cheaper, coarser) — still applies the full rubric.

## Ownership table (each law scored once)

| Law | File (`references/laws/…`) | Owner area |
|---|---|---|
| Hick's Law | `hicks-law.md` | IA |
| Choice Overload | `choice-overload.md` | IA |
| Miller's Law | `millers-law.md` | IA |
| Chunking | `chunking.md` | IA |
| Working Memory | `working-memory.md` | IA |
| Jakob's Law | `jakobs-law.md` | IA |
| Serial Position Effect | `serial-position-effect.md` | IA |
| Law of Similarity | `law-of-similarity.md` | Visual |
| Law of Proximity | `law-of-proximity.md` | Visual |
| Law of Common Region | `law-of-common-region.md` | Visual |
| Law of Uniform Connectedness | `law-of-uniform-connectedness.md` | Visual |
| Law of Prägnanz | `law-of-pragnanz.md` | Visual |
| Von Restorff Effect | `von-restorff-effect.md` | Visual |
| Aesthetic-Usability Effect | `aesthetic-usability-effect.md` | Visual |
| Selective Attention | `selective-attention.md` | Visual |
| Doherty Threshold | `doherty-threshold.md` | Interaction |
| Fitts's Law | `fittss-law.md` | Interaction |
| Goal-Gradient Effect | `goal-gradient-effect.md` | Interaction |
| Peak-End Rule | `peak-end-rule.md` | Interaction |
| Zeigarnik Effect | `zeigarnik-effect.md` | Interaction |
| Flow | `flow.md` | Interaction |
| Postel's Law | `postels-law.md` | Forms |
| Tesler's Law | `teslers-law.md` | Forms |
| Parkinson's Law | `parkinsons-law.md` | Forms |
| Cognitive Load | `cognitive-load.md` | Forms |
| Occam's Razor | `occams-razor.md` | Forms |
| Mental Model | `mental-model.md` | advisory (unscored) |
| Paradox of the Active User | `paradox-of-the-active-user.md` | advisory (unscored) |
| Pareto Principle | `pareto-principle.md` | advisory (unscored) |
| Cognitive Bias | `cognitive-bias.md` | advisory (unscored) |

See `references/laws/README.md` for the family-grouped index of all 30 files.
