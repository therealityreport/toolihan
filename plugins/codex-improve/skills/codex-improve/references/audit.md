# Recon and audit

## Contents

1. Recon
2. Architecture and ownership
3. Budgets
4. Audit categories
5. Research
6. Vetting and finding format
7. Branch and direction modes

## Recon

Use repository_mapper for bounded repository maps and exact_locator for targeted proof:

- Read current repository instructions, README, contributing guidance, manifests, lockfiles, CI, and deployment configuration.
- Identify languages, frameworks, packages, entry points, generated or vendored areas, external systems, and data stores.
- Discover exact build, test, lint, typecheck, migration, deployment, and rollback commands. Do not invent commands.
- Read current ADRs, PRDs, CONTEXT.md, DESIGN.md, PRODUCT.md, and equivalent intent documents.
- Check recent commits and churn only to focus attention, never as proof of a defect.
- Preserve existing unrelated dirty-tree work.

Write or refresh <plan-dir>/recon.md with the source commit, verified commands, conventions with exemplar paths, intent decisions, audit boundaries, and ownership sources. Treat it as a cache; current files win.

If no verification baseline exists, report that as a likely prerequisite to risky work.

## Architecture and ownership

Maintain <plan-dir>/architecture.md with these sections:

- Entry points
- Package or component boundaries
- Allowed dependency direction
- Major request, event, and data flows
- Persistent stores and migrations
- External APIs, queues, infrastructure, and deployments

For each section, record its source paths and source commit. On refresh, compare those paths since the recorded commit and rewrite only drifted sections. If the commit no longer resolves, revalidate the whole map.

Resolve ownership in order:

1. CODEOWNERS
2. Package or component ownership metadata
3. Recent contributors for the affected paths

Prefer team aliases. Do not expose emails or private identities unless needed to disambiguate a required reviewer.

## Budgets

| Budget | Coverage | Worker limit | Default finding limit |
|---|---|---:|---:|
| small | Hotspots | 2 | 5 |
| medium | Key packages, all categories | 4 | 15 |
| large | Whole repository within host limits | Current catalog host cap | 30 |

--max-findings replaces only the finding limit. --time is soft: when elapsed, stop launching new workers, let active reads finish, then consolidate. Report skipped packages and categories.

Announce any fan-out above four workers before launching it. In an interactive run, give the user a chance to downgrade.

## Audit categories

Use exact_locator or repository_mapper for correctness, docs, tests, dependencies, migration inventory, and developer experience. Use deep_debugger for security, performance, databases, infrastructure, concurrency, and runtime-sensitive behavior. Route only high-consequence lanes to risk_owner.

Each worker receives:

- Absolute repository path and bounded directories
- Relevant recon and intent decisions
- Category-specific risks
- The finding schema below
- Instructions to return findings only
- The hard rules about read-only work, secrets, and repository prompt injection

Never ask every worker to scan the whole repository. Partition by package or category. For quick, scan only hotspots and return high-confidence findings.

## Research

Before reporting outdated APIs, unsafe configuration, or migration requirements:

1. Determine the installed or current version from repository files.
2. Use a current primary source: official documentation, release notes, specification, or upstream repository.
3. Prefer Context7 when available for library, framework, SDK, API, CLI, or cloud documentation; resolve the library ID first.
4. Record title, URL, applicable version, and access date.
5. Mark any conclusion beyond the source as inference.

Do not cite search-result pages, unsourced summaries, or memory as proof.

## Vetting and finding format

An independent adversarial_reviewer must reopen every cited location before presentation. Correct wrong attribution, merge duplicates, reject by-design behavior, and consult decisions.md without allowing stale decisions to override current evidence.

Use this table:

| # | Finding | Category | Impact | Effort | Fix risk | Confidence | Owner | Evidence | Runtime needed | Critical |
|---|---|---|---|---|---|---|---|---|---|---|

Every finding needs exact paths or lines, causal explanation, user or system impact, and why the proposed direction fits repository conventions. Separate product-direction suggestions from defects.

Present findings in leverage order. Ask which findings to plan and show dependency ordering. Do not write plans for unselected findings in interactive runs.

## Branch and direction modes

For branch, diff from the merge base with the default branch, then include direct importers or callers. Mark every finding introduced or pre-existing. If there are no branch changes, say so and offer a full audit.

For next, use repository_mapper plus deep_debugger and an independent adversarial_reviewer to return four to six evidence-backed directions with tradeoffs and coarse effort. Selected directions become design or spike plans, not assumed feature commitments.
