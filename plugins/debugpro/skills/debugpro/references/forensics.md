# Debugging Forensics

Use when evidence may disappear, multiple actors changed state, or the order of
events matters more than immediate fixing.

## Preserve First

- Current file diffs, process list, logs, traces, screenshots, and failing command output.
- Versions, timestamps, deploy IDs, commit SHAs, branch names, and config checksums.
- Tool errors and repeated-failure pairs.
- Ownership notes when other agents or users are editing nearby surfaces.

## Timeline

1. Last known good signal.
2. First observed bad signal.
3. Changes between those points.
4. Probes already run and their outcomes.
5. Current blocker or supported cause.

## Rules

- Do not clean up artifacts before capturing the evidence they contain.
- Do not overwrite another worker's edits to recreate a cleaner state.
- Label speculation separately from observed facts.
- Prefer append-only notes for handoff when the system is still changing.
