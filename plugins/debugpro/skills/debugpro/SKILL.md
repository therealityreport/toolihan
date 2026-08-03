---
name: debugpro
description: Use when failures need evidence-first root-cause routing.
---

# DebugPro

Root router for evidence-first debugging. Current files and live signals are authoritative.

## Capability Selection

For broad, mixed, or tool-dependent requests, consult `references/capability-router.md` before selecting a route. Use it to choose the right skills, agents, references, tools, CLIs, MCPs, connectors, fallbacks, and stop conditions.

If the route is still ambiguous, use `debugpro-capability-router` to produce a compact routing packet before diagnosis or delegation.

## Popup Intake Gate

Follow the user-level requesting-user-input contract. Prefer the User Questions Tweaker's `user_questions` tool when available, then native `request_user_input`, and use concise chat only when neither structured tool can represent the required input. Ask only when the first route is ambiguous or evidence is missing after checking current source, logs, tests, runtime signals, and user-provided facts. Do not prompt when existing source, log, test, or runtime evidence already proves the route.

The first intake must collect these three user-owned answers:

- Symptom/impact.
- Reproduction or evidence source.
- Safety boundary or desired next action.

Add other independent, material decisions to the same 4-6-question User Questions round when they are already known; never invent filler questions to reach the normal round size. Require the three core answers before proceeding unless an explicit exception is recorded with the reason, missing answer, and safest evidence-backed route. Record the tool, logical round, selection mode, and answers in DebugPro output or handoff under `User input rounds`.

## Operating Loop

1. Capture symptom, impact, signal, environment, scope, and exact evidence.
2. Prove or bound the root cause before proposing fixes.
3. Use the smallest useful evidence loop first.
4. Form falsifiable hypotheses when needed; probe one at a time unless safe parallel escalation is justified.
5. Fix only after evidence supports the cause, then verify against the original symptom.

Do not guess, broaden scope, run destructive cleanup, or claim diagnosis without evidence. Shared execution contract: `references/debugging-discipline.md`.

## Routing

- `debugpro-intake` for missing context.
- `debugpro-hypotheses` for unclear causes.
- `debugpro-team` for safe independent read-only tracks.
- `debugpro-production-debugging` when observability is central.
- `debugpro-arbitration` after competing investigation results exist.
- `debugpro-adjacent-sweep` after an approved fix.
- `debugpro-bug-hunt` for review-only bug finding, diff audits, stack trace triage, event triage, or bounded static inspection.

Use `references/routing.md` for the DebugPro skill matrix, `references/evidence-modes.md` for proof-loop selection, `references/output-contracts.md` for reports, and `references/technique-index.md` for deeper method selection. Prefer a more specific local debugging skill when it owns the task.

## Handoff

Use `references/handoff-report-template.md` unless the user requested a different format.

## Shared Evidence

When a finding should be handed to Plan Grader, comprehensive review, or another DebugPro run, export it as `shared-evidence.v1.json` using `references/shared-evidence-contract.md`. Validate packages with `scripts/validate_shared_evidence.py` before relying on them as machine-readable evidence.

Use `scripts/export_shared_evidence.py --input findings.json --output shared-evidence.json` when a DebugPro workflow has explicit finding objects and needs a validated JSON or JSONL package for another plugin.
