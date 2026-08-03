---
description: Apply one fix from a prior /ux-audit report. Re-confirms the evidence, shows the exact diff, and is dry-run by default — it only edits after you pass --apply and confirm. One fix at a time; never bulk. Structural (larger-effort) fixes are described, not auto-applied.
allowed-tools: Read, Grep, Glob, Edit
argument-hint: "<finding-id | law-name | file:line> [--apply]"
---

Apply a single, high-confidence fix from a Laws-of-UX audit. Target: `$ARGUMENTS`.

Read the `laws-of-ux` skill for the law's intended fix pattern before touching anything.

## Procedure

1. **Resolve the finding.** From `$ARGUMENTS`, identify the finding by its id, law name, or
   `file:line`. If ambiguous or you don't have the prior report in context, ask the user to run
   `/ux-audit` first or to name the exact file:line and law.

2. **Re-read the target file and confirm the evidence still matches** (guard against drift since
   the audit). If the code no longer matches the finding, stop and report that — do not edit.

3. **Only quick-wins are auto-applicable.** If the finding is tagged `larger-effort`
   (structural / IA / routing), do **not** edit. Describe the change and the steps instead, and
   stop.

4. **Show the exact diff** (before/after) for the minimal change. Explain what law it satisfies
   and why it's safe.

5. **Dry-run by default.** Without `--apply`, stop here — show the diff, make no edit.

6. **Apply only with `--apply` and explicit confirmation.** With `--apply`, ask the user to
   confirm, then make **one** minimal `Edit`. Never batch multiple fixes; run the command again
   for the next one. After editing, restate what changed and suggest re-running `/ux-audit` to
   confirm the score moved.

## Rules
- One fix per invocation. No bulk apply.
- Never widen scope beyond the single finding.
- If applying could plausibly break behavior (not a pure UX-attribute change), flag the risk and
  default to describing rather than editing.
