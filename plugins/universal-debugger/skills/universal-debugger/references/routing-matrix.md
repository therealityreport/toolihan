# Routing Matrix

Universal Debugger decides the investigation lane, collects missing intake, and keeps root-cause discipline. It should not replace the existing debugging skills once a better-matched skill is clear.

## Prompt Routing

| Prompt shape | Primary route | Why |
| --- | --- | --- |
| "Debug this", failing test, exception, active regression, broken route, production incident, unexplained behavior | `master-debugger` | Active failures need a reproduction loop, root-cause proof, and one fix at a time. |
| "Find bugs", "review for bugs", branch diff audit, stack trace triage, Sentry event triage, or "check what else this fix breaks" | `find-bugs-plus` | Bug hunts need evidence-backed findings and same-family adjacent sweeps during approved fixes. |
| "How should I debug...", "what profiler/debugger/logs should I use", crash dump reading, checklist request | `debugging-strategies` | The user is asking for technique or diagnostic strategy rather than direct incident ownership. |
| Intermittent or cross-boundary failure with several plausible causes, or a request to compare hypotheses | `parallel-debugging` | Competing explanations need independent evidence and arbitration before the fix path is chosen. |
| User explicitly asks for Superpowers, systematic debugging, the four phases, or Superpowers stop rules | `superpowers:systematic-debugging` | The requested process has its own contract and terminology. |
| Potential issue with no observable failure yet | Stay in `universal-debugger` for intake, then route | First identify the risk signal, expected failure mode, and available evidence. |
| Root cause is already proven and the user asks only for implementation | Do not keep routing as a debugging task | Confirm the evidence briefly, then use the appropriate implementation workflow. |

## Conflict Rules

1. Explicit user invocation wins when it is relevant and safe.
2. Active unresolved failures route to `master-debugger` before general strategy guidance.
3. Bug-finding requests route to `find-bugs-plus`; if it discovers an unresolved active failure, hand root-cause ownership to `master-debugger`.
4. When implementation is requested, `find-bugs-plus` runs a bounded adjacent-defect sweep on the same touched surface before final verification.
5. Technique-only questions route to `debugging-strategies`, even if the examples mention bugs.
6. Multiple credible root-cause hypotheses can use `parallel-debugging` as an overlay, then return confirmed findings to `master-debugger` or the active workflow.
7. Explicit Superpowers or strict four-phase language routes to `superpowers:systematic-debugging`.
8. Parallel agents are never implied. Use them only after explicit user permission; otherwise investigate tracks sequentially.
9. If reproduction, logs, tests, code access, or environment details are missing, stay in intake and name the blocking gap.

## When To Stay Here

Stay in this skill while the task is still about:

- deciding which debugging skill should own the work
- turning a vague symptom into a complete issue intake
- setting evidence standards before investigation starts
- producing a concise handoff across debugging skills

Leave this skill once the route is clear and the downstream skill's workflow should take over.
