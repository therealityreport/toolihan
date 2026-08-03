# Shared Evidence Contract

DebugPro and Plan Grader use `shared-evidence.v1.json` to exchange sourced findings without scraping Markdown reports.

## When To Use

- Export a DebugPro finding for Plan Grader scoring or handoff validation.
- Import a Plan Grader finding into a debugging route.
- Preserve source evidence while avoiding duplicate review, grading, or reproduction work.

## Required Fields

- `runId`: stable producer run id.
- `sourcePlugin`: plugin that created the finding.
- `findingId`: stable id inside that run.
- `severity`: `blocker`, `critical`, `high`, `medium`, `low`, or `info`.
- `claim`: concise finding.
- `evidence`: sourced evidence entries.
- `affectedFiles`: related paths.
- `recommendedNextStep`: next action.
- `status`: `open`, `accepted`, `deferred`, `resolved`, or `rejected`.

## Safety Rules

- Redact secrets, cookies, bearer tokens, API keys, session ids, and private chat content.
- Prefer short evidence summaries, file paths, line numbers, command names, and test names.
- Put long logs or screenshots in plugin-specific evidence bundles and reference them by path.

Validate a package with:

```bash
python3 scripts/validate_shared_evidence.py skills/debugpro/references/shared-evidence.v1.example.json
```
