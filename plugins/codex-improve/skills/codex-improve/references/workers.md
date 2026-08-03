# Universal role routing

Codex Improve consumes the global universal role catalog. The catalog, not this plugin, owns current models, reasoning effort, developer instructions, and registration. This plugin maps workflow responsibilities to catalog role names in assets/universal-role-mappings.json.

Before the first dispatch, run the global doctor:

    python3 ~/.codex/skills/subagent-routing/scripts/sync-universal-roles.py --check --json

If the doctor reports drift, an unavailable catalog, an unrecognized role, or a missing host route, stop and return BLOCKED for explicit reassignment. Do not create a local .codex/agents directory, copy a role file, or invent a fallback.

## Responsibility mappings

| Responsibility | Universal role or roles | Selection rule |
|---|---|---|
| Scope and triage | senior_scout; risk_owner | Use senior_scout normally and risk_owner for high-consequence work. |
| Recon and architecture mapping | repository_mapper; exact_locator | Map bounded systems first, then collect exact proof. |
| Bounded audit and evidence collection | exact_locator; repository_mapper | Partition paths and categories into non-overlapping assignments. |
| Specialist investigation | deep_debugger; risk_owner | Use deep_debugger for coupled technical analysis and risk_owner for critical lanes. |
| Plan authoring and migration design | senior_scout; risk_owner | Escalate only the critical or migration lane. |
| Evidence judgment and plan critique | adversarial_reviewer; implementation_reviewer | Keep the reviewer independent from the author or implementer. |
| Approved plan execution | feature_implementer; large_implementer | Use the smallest implementation role that fits the frozen plan. |
| Mechanical follow-up | mechanical_editor; bounded_fixer | Use the narrowest predictable or corrective role. |
| Final acceptance and recovery | acceptance_integrator; recovery_lead | Use recovery_lead only after ordinary routes have failed. |

Run mechanical verification directly. Do not spawn a model for deterministic pass or fail commands.

## Legacy terminology

The old Codex Improve names are documentation-only mappings:

| Old responsibility | Universal owner |
|---|---|
| Workflow lead | Parent task |
| Recon mapping | repository_mapper |
| Bulk audit | Parallel exact_locator assignments with separate scopes |
| Specialist audit | deep_debugger or risk_owner |
| Evidence and plan review | adversarial_reviewer |
| Plan authoring | senior_scout; Plan Architect remains its named narrower exception |
| Execution | bounded_fixer, feature_implementer, or large_implementer |
| Risky execution | risk_owner |
| Final critical judgment | acceptance_integrator prepares evidence; parent retains final acceptance |

These names are not registered aliases and must never become project worker files.

## Tier and concurrency behavior

| Tier | Scope | Maximum parallel dispatch |
|---|---|---:|
| quick | Hotspots and high-confidence findings | 2 |
| standard | Key packages and all relevant categories | 4 |
| deep | Whole repository within the current global host cap | Current catalog host cap |
| critical | One high-consequence lane at a time | Serial implementation |

The effective worker limit is the lowest of the tier limit, budget limit, current catalog limit, and host limit. The selected universal role fixes the model and effort; do not override either field in a dispatch.

## Luna gate

The global catalog owns the gpt-5.6-luna gate. Codex Improve does not request Luna directly. A future mapping may use that route only when runtime.gatedModels.gpt-5.6-luna.status is proven. If it is unavailable or unproven, report BLOCKED for explicit reassignment; do not generate a project role file or silently substitute another model.

## Critical routing

Mark a finding critical if it touches any of:

- Authentication, authorization, or secrets
- Payments or financial calculations
- Destructive database migrations
- Data deletion or irreversible transformations
- Production infrastructure or deployment permissions
- Cryptography, sandboxing, or command execution
- Race conditions or distributed state

For that lane, have risk_owner validate the safety and rollback boundary, use large_implementer only after approval in an isolated worktree, and have acceptance_integrator perform final readiness review. Leave unrelated lanes at the selected tier.

## Dispatch contract

Every dispatched assignment must name the selected universal role, its bounded ownership, dependencies, current catalog health, expected checks, stop conditions, and return contract. A route that cannot expose the named role is unavailable. Report it rather than silently changing role, model, effort, dispatch, ownership, or scope.
