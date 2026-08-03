---
name: improve-tool
description: Improve an existing local or fetched tool asset after Tool Finder has selected a candidate.
---

# Improve Tool

Improve a selected tool asset with a local-first patch plan.

Allowed v1 destinations:

- Current workspace.
- Explicitly selected local plugin path.
- Explicitly selected local skill path.

Default output:

- Gap report.
- Patch plan.
- Local edits only when destination is explicit.
- Validation commands and expected results.

Do not write to remote GitHub in v1. Do not edit cached third-party plugin copies unless the user explicitly selects that path and understands it may be overwritten.
