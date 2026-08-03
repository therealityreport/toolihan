---
description: Audit a frontend project against the 30 Laws of UX. Detects the UI stack, dispatches concern-area auditor subagents, scores each applicable law from source-code signals, and prints a graded report (0-100 + A-F) with a findings table and a prioritized quick-wins-vs-larger-efforts fix list. Static and read-only by default; --url adds a live browser/Lighthouse pass, --html renders an HTML scorecard.
allowed-tools: Read, Grep, Glob, Task, Bash(git ls-files:*), Bash(rg:*), Bash(find:*), Bash(ls:*), Bash(cat:*), Bash(cp:*), Bash(mkdir:*)
argument-hint: "[path] [--url <addr>] [--html] [--out <file>] [--area ia|visual|interaction|forms|all] [--quick]"
---

Audit the target against the 30 Laws of UX and produce a graded report with prioritized,
code-level fixes. Arguments: `$ARGUMENTS` (default target = current repo root / cwd).

**First, load the knowledge base.** Read the `laws-of-ux` skill (`skills/laws-of-ux/SKILL.md`)
and follow its rubric exactly. It is the single source of truth. Do not grade from memory of
the laws — use the reference files, especially `references/scoring-rubric.md`.

## Flags
- `--url <addr>` — also run the live pass on a running app (see `references/live-audit.md`).
- `--html` — also render the HTML scorecard (`templates/scorecard/`).
- `--out <file>` — write the Markdown report to `<file>` (otherwise print inline).
- `--area ia|visual|interaction|forms|all` — limit to one concern area (default `all`).
- `--quick` — single combined pass, no subagent fan-out (cheaper, coarser). Still full rubric.

## Procedure

1. **Resolve scope.** Parse `$ARGUMENTS` for the path/URL and flags. If a bare URL is given
   with no path, treat it as `--url` against that address.

2. **Detect the stack** using `references/stack-detection.md` (read `package.json`, config
   files, route dirs, styling deps, component libraries). Record stack + the file globs to scan.
   **If there is no frontend surface** (backend-only / library / docs repo), STOP and print the
   polite no-frontend refusal from `stack-detection.md`. Emit **no grade**.

3. **Enumerate the UI surface** (components, tokens/styles, nav/routing, forms, buttons,
   async/loading code). On a large repo, **sample** per `stack-detection.md` and record what you
   sampled so the report can state it. Credit design-system primitives (shadcn/Radix/MUI/Chakra)
   but still audit composition.

4. **Audit.** Unless `--quick`, dispatch the `ux-auditor` subagent once per in-scope concern
   area (IA, visual, interaction, forms) via the Task tool, passing each: the `concern_area`,
   the resolved file globs, the detected stack, and the sampling note. Each returns a strict
   structured block per law (`law, applicable, ordinal, confidence, severity, evidence[],
   recommendation, fix_snippet, effort`). Run the four passes in parallel when possible. With
   `--quick`, do the passes yourself in one sequence.

5. **Live pass — only if `--url`.** Follow `references/live-audit.md` using the connected
   chrome-devtools MCP (load its tools via ToolSearch `query: "chrome-devtools"` if deferred).
   Measure Doherty (Lighthouse/traces → real LCP/INP), Fitts's (`getBoundingClientRect`),
   Aesthetic-Usability/Prägnanz/Gestalt/Selective-Attention (screenshots), Von Restorff
   (computed styles). Set `c = 1.0` and basis `live` for each measured law; live overrides
   static. If no chrome-devtools MCP is connected or the URL won't load, skip the live pass, say
   so, and keep the static grade.

6. **Verify every finding.** Enforce the two-stage rule from `scoring-rubric.md`: re-open the
   cited file and confirm the evidence (check for framework/library provision) before a finding
   counts. Drop unconfirmable candidates to a "Needs review" advisory — they must not move the
   grade. **No `file:line`, no grade impact.**

7. **Synthesize + render.** Dispatch the `ux-synthesizer` agent (Task) with all auditor outputs,
   the live measurements (if any), the detected stack, the sampling note, and the `--html` /
   `--out` flags. It applies `references/scoring-rubric.md` (classify APPLICABLE / N/A /
   NOT_ASSESSED, dedupe composites, confidence-weighted per-category + overall roll-up, coverage
   band, and the severity-then-effort fix ordering), renders `templates/report-template.md`, and —
   with `--html` — writes the `templates/scorecard/` HTML + CSS to the output folder
   (`<target>/ux-audit/` or the `--out` directory). It reads `.lawsofux.json` overrides if
   present. In `--quick` mode you may run the synthesis inline instead of dispatching the agent.

8. **Close.** Print the report (and any written file paths), then point to `/ux-fix <finding>`
   (apply one fix, dry-run first) and `/ux-explain <law>`.

## Rules
- Read-only. Never edit project files in this command — fixes are emitted as snippets/diffs only.
- Be honest: state what you could not assess. Never invent a violation to fill a category.
  Never emit a grade for a repo with no frontend.
