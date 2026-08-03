# Execute, verify, reconcile

## Contents

1. Preconditions
2. Conflict graph
3. Dispatch
4. Mechanical verification and review
5. Batch execution
6. Status and reconciliation
7. Decision learning

## Preconditions

Before any execution:

- Require a Git repository and a resolvable planned-at commit.
- Ensure the plan is approved and status is TODO or deliberately retried BLOCKED.
- Re-run its drift check. Reconcile stale excerpts or scope first.
- Verify backup and rollback prerequisites for risky work.
- Obtain fresh approval for the plan or explicit batch.
- Verify the universal catalog with the global doctor and confirm the named role is available.

Do not execute a plan directly on the original branch.

## Conflict graph

Before a range or all, compare TODO plans by:

- Paths
- Symbols and configuration keys
- Database migrations
- API or schema changes
- Dependency upgrades
- Declared dependencies

Create graph edges and classify them:

- Depends: reorder the dependent plan after its prerequisite.
- Compatible overlap: serialize and re-run drift checks between plans.
- Incompatible: block both from batch execution and request one combined or revised plan.

Critical plans always execute individually. A DONE dependency must also be merged into the batch base; otherwise skip its dependents.

## Dispatch

Create <repo>/.worktrees/codex-improve-NNN on branch codex-improve/NNN-<slug> from the current default-branch base. Never reuse a dirty or unrelated worktree.

Select feature_implementer for one routine frozen plan. Select large_implementer for a multi-package, terminal-heavy, or higher-complexity plan. Have risk_owner own high-consequence safety and rollback boundaries before implementation. If the exact universal role is unavailable, return BLOCKED for explicit reassignment.

Every implementation assignment receives:

- Full plan text, inlined
- Worktree path
- In-scope and out-of-scope paths
- STOP conditions and rollback boundary
- Repository instruction paths
- Secret and prompt-injection hard rules
- Required deterministic checks and return contract

The implementation role must stop before an irreversible step when backups or rollback prerequisites are unverified. It returns a typed status, concise changed-file and behavior summary, command-to-result checks, STOP evidence when applicable, actual role and effort, and risks or follow-up facts.

## Mechanical verification and review

Run deterministic checks directly in the worktree:

1. Diff, status, and out-of-scope path check
2. Plan-specific tests
3. Type checks, lint checks, builds, or migrations in check or dry-run mode
4. Runtime verification when it is a done criterion and read-only access exists

Do not ask a model to run or interpret simple pass or fail commands. Capture exact failures.

Have adversarial_reviewer read every diff hunk and verified result. Use acceptance_integrator for deep or critical final readiness. Verdicts:

- APPROVE: scope clean, intent met, all criteria pass. Mark DONE and report branch or worktree; merging remains the user's choice.
- REVISE: give the implementation role precise evidence-backed feedback in the same worktree.
- BLOCK: STOP condition, unrecoverable scope violation, unsafe assumption, unavailable route, or two failed revisions. Mark BLOCKED and have the plan author rewrite the plan before any retry.

Never allow more than two implementation revision rounds.

## Batch execution

Execute serially in graph order. After each plan, complete the full independent review verdict and refresh remaining drift checks. Continue independent siblings after a BLOCK, but skip all dependents with a recorded reason.

Finish with plan, verdict, worktree, branch, selected role, catalog health, and dependency status. Never merge automatically.

## Status and reconciliation

status reads artifacts only. Report DONE, BLOCKED with reason, stale IN PROGRESS, conflicts, and TODO plans whose dependencies are merged. Do not audit or run verification.

reconcile:

- Spot-check recon.md commands and refresh drifted entries.
- Refresh only drifted architecture.md sections.
- Verify DONE outcomes still exist.
- Investigate BLOCKED plans and revise or reject them.
- Mark stale plans and retire independently fixed findings.
- List worktrees. Remove only worktrees whose branches are merged; ask before touching unmerged work.
- Propose closing published issues rather than closing without authorization.

## Decision learning

Maintain <plan-dir>/decisions.md entries with:

- Stable finding fingerprint: category plus normalized behavior plus primary paths
- Outcome: accepted, rejected, revised, ineffective, or fixed independently
- Concise reason
- Decision commit or date
- Superseding plan or evidence, when any

During later vetting, suppress materially identical rejected findings only when evidence and intent are unchanged. Prefer successful approaches, flag repeated ineffective ones, and reopen any decision whose paths, requirements, or evidence drifted.
