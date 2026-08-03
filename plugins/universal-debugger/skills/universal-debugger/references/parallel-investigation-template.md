# Parallel Investigation Template

Use parallel investigation only for independent hypotheses that can be checked without contaminating each other. Parallel agents require explicit user permission. Without that permission, keep the same hypothesis structure but investigate sequentially.

## Permission Boundary

Before assigning parallel agents, confirm:

- the user explicitly allowed parallel agents or subagents
- each track has a distinct hypothesis and bounded search area
- each track can report evidence without making fixes
- the main agent will arbitrate results before any implementation

Do not imply that this plugin can spawn agents by itself. It can only instruct the current orchestrator to use an available parallel workflow when allowed.

## Investigator Packet

Give each investigator:

```text
Symptom:
Known reproduction or evidence signal:
Hypothesis to test:
Files/systems in scope:
Files/systems out of scope:
Confirming evidence:
Falsifying evidence:
Allowed commands or probes:
Stop condition:
Required report format:
```

Each investigator should test only its assigned hypothesis. It should not fix the issue, broaden scope, or rewrite shared code.

## Evidence Report

Each track reports:

```text
Hypothesis:
Status: confirmed | plausible | falsified | inconclusive
Evidence:
Commands/probes run:
Relevant files, lines, logs, traces, or test names:
Contradictions or gaps:
Recommended next probe:
```

## Arbitration

Arbitrate before fixing:

1. Prefer evidence from a direct reproduction, failing test, trace, debugger inspection, database query, or deterministic command.
2. Treat code reading without a reproduced signal as weaker evidence unless the defect is mechanically obvious.
3. Mark contradictions explicitly instead of smoothing them over.
4. Choose the hypothesis that explains the original symptom with the fewest unsupported assumptions.
5. If no hypothesis is confirmed, generate new hypotheses from the collected evidence rather than guessing a fix.

Once a cause is confirmed, hand it to `master-debugger` or the active debugging workflow for one minimal fix and verification.
