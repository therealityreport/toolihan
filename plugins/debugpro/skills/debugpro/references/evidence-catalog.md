# Evidence Catalog

Use to decide which proof is strong enough for diagnosis or completion.

## Strong Evidence

- Reproducible command or user action tied to the original symptom.
- Failing and then passing test for the same behavior.
- Source path and code path proving the data/control flow.
- Runtime logs, traces, metrics, request IDs, or crash reports for the failing event.
- Browser screenshot/console/network proof for a UI symptom.
- Source/runtime diff proving stale or wrong executing artifact.

## Medium Evidence

- Correlation with deploys, config changes, dependency updates, timing, or cohorts.
- Warnings near the failure that match the suspected path.
- Partial local reproduction that differs from production in known ways.

## Weak Evidence

- Anecdote, intuition, broad pattern match, or an unrelated passing check.
- Search absence such as "no references found" without runtime proof.
- A fix that appears plausible but was not checked against the original signal.

## Completion Rule

For `DONE`, include at least one strong evidence item for the cause or the fix.
For `DONE_WITH_CONCERNS`, state which evidence remains medium or missing.

## Related References

- `evidence-modes.md` selects the proof loop for diff review, failure investigation, event triage, static bug hunts, and adjacent sweeps.
- `output-contracts.md` defines report shapes for findings, fixes, and incidents.
- `secret-redaction.md` defines what must be sanitized before quoting logs, traces, env dumps, API errors, MCP diagnostics, proxy output, or browser/session artifacts.
