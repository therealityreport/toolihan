# Planning, migrations, and publishing

## Contents

1. Plan workflow
2. Required plan contract
3. Critical and migration requirements
4. Plan criticism
5. Index and conflicts
6. Security and issues

## Plan workflow

Before writing, record the current short commit SHA and read existing plan artifacts. Keep numbering monotonic, avoid duplicates, and preserve prior statuses.

Use senior_scout to author ordinary plan text from personally verified evidence. Use risk_owner for critical or migration design. Have a separate adversarial_reviewer or implementation_reviewer cold-read the result. The orchestrator writes only accepted text under the chosen plan directory.

For plan <description>, skip the broad audit, run focused recon, resolve discoverable ambiguity from current files, and ask only decisions that materially change the plan.

## Required plan contract

Each NNN-<slug>.md must contain:

1. Imperative title and status: TODO, IN PROGRESS, DONE, BLOCKED, REJECTED, or STALE
2. Planned-at commit and date
3. Why the change matters
4. Current state with verified excerpts and evidence
5. Primary documentation sources with version and access date, when applicable
6. In-scope and explicitly out-of-scope paths or behaviors
7. Ownership and suggested reviewers
8. Exact commands the implementation role needs
9. Ordered implementation steps; each step ends with a command and expected result
10. Test plan following an existing repository pattern
11. Machine-checkable done criteria
12. Dependencies and known conflicts
13. Specific STOP conditions
14. Maintenance notes

Inline enough context for a fresh universal implementation role. Never write as discussed above. Stamp excerpts and in-scope paths for drift checking.

## Critical and migration requirements

For any critical lane, add:

- Required backups and how to verify them
- Irreversible steps
- Last safe stopping point
- Rollback commands
- Rollback verification
- Production permission requirements

For migrate <target>, also add:

- Current and target versions or systems
- Compatibility matrix
- Breaking changes and deprecations from primary sources
- Data and configuration transformations
- Mixed-version constraints and staged rollout
- Compatibility tests

If rollback is impossible, state that plainly and require explicit approval immediately before the irreversible step.

## Plan criticism

The independent reviewer reads the plan without relying on the authoring conversation and checks:

- Can a fresh universal implementation role act without choosing architecture or product behavior?
- Are scope, commands, expected results, and test locations exact?
- Do STOP conditions cover likely drift and unsafe assumptions?
- Does every risky step have a verified rollback boundary?
- Are cited docs and current code consistent?
- Do dependencies and conflicts match other plans?

Return concrete edits. The plan author revises once before presentation. review-plan <file> applies this process to an existing plan and updates it only with user authorization.

## Index and conflicts

Maintain <plan-dir>/README.md with:

- Recommended order
- Status table
- Dependency graph
- Conflict notes
- Worktree, branch, and issue links
- Findings considered and rejected

Record paths, symbols, config keys, schema or API changes, migrations, and dependencies each plan expects to modify. These fields feed batch conflict detection.

## Security and issues

Before writing sensitive security details into a public repository, warn the user and obtain confirmation or use a user-selected ignored directory. In non-interactive public runs, record a redacted finding and withhold sensitive plan detail.

With --issues:

1. Verify gh auth status, the GitHub remote, and repository visibility.
2. Preview issue titles.
3. Obtain one publishing confirmation.
4. Require separate explicit confirmation for sensitive public content; otherwise skip it.
5. Record created URLs or skip reasons in the plan index.

The flag authorizes issue creation only. It does not authorize source edits, pushes, or merges.
