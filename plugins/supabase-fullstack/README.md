# Supabase Fullstack

This plugin replaces the local `supabase-expert` and `supabase-agent-skills` plugins with one improved multi-skill bundle.
It also carries forward Claude-compatible plugin metadata so the same bundle can be reused across Codex and Claude plugin surfaces.

Supabase Fullstack is the connector-aware command surface for Supabase work. It starts from the live Supabase App connector when hosted project state matters, then applies local review, routing, and customization guidance for RLS, Auth, Storage, migrations, Postgres performance, and project conventions.

Install and use this as the user/system-level Supabase plugin. Do not split the marketplace capabilities into one-off project-level plugins unless a project truly needs a narrower override.

It does not replace the official `supabase@openai-curated` plugin or the shared Supabase App for live project access. Both plugins point at the same Supabase App connector ID. When a task needs hosted Supabase project state, SQL execution, advisors, storage buckets, Edge Functions, branches, or deployed settings, use the live Supabase App connector first, then use these skills to interpret and harden the result. If the connector is missing, unloaded, unauthenticated, or otherwise not callable, continue from local files and explicit CLI/database evidence without claiming live hosted verification.

Do not add custom skills, marketplace aggregation, or project-specific behavior to the OpenAI-built Supabase connector. Those additions belong in this `supabase-fullstack` plugin.

## Skills

- `supabase-command-surface`: single live-project entrypoint that checks Supabase App connector status, uses live project tools first when hosted state matters, and routes into the local review playbooks
- `supabase-fullstack-review`: broad project review and routing across security and performance concerns
- `supabase-security-governance`: RLS, Auth, Storage, migrations, SSR/server boundaries, and security audits
- `supabase-postgres-performance`: schema design, indexing, query tuning, locking, monitoring, and RLS performance guidance

## Routing Rule

Use `$supabase-command-surface` first for broad Supabase work.

- Use the shared Supabase App connector for live Supabase project access and operations.
- Use `supabase-fullstack` skills for local code, marketplace-skill routing, migration, RLS, auth, storage, project conventions, and performance review.
- Use both when the best answer needs live project evidence plus stricter security or performance interpretation.
- If the connector is installed but tools are not callable, report the connector/auth/session blocker instead of claiming live project verification.

## Plugin vs App

- `@supabase` is the official plugin bundle: metadata, upstream Supabase skills, and the shared Supabase App connector.
- `$supabase` is the app/connector itself: the callable live-project tool surface for projects, SQL, migrations, branches, logs, advisors, Edge Functions, keys, and project settings.
- `@supabase-fullstack` is the editable local command surface: it depends on the same `$supabase` app for live state and adds local routing, conventions, review playbooks, and safety checks.

## Supabase Marketplace Sources

This plugin should preserve and route the useful capabilities from all three Supabase marketplace sources:

- `supabase/agent-skills`: broad Supabase coverage, Postgres best practices, and skill authoring.
- `supabase/server`: server-side auth, request contexts, `@supabase/server`, Edge Functions, and server/client boundary guidance.
- `supabase/supabase`: Studio-originated skills for safe SQL, Vitest, React composition, queries, testing, error handling, UI patterns, telemetry, E2E, and mock API tests.

Treat these as capability sources for this local plugin. Do not assume a source skill applies directly to every project; the command surface should route it through local project rules first.

## Startup Status Check

At the start of Supabase work, the command surface should identify:

- Whether the shared Supabase App connector tools are callable in the current thread
- Whether the official Supabase plugin is installed and enabled when plugin metadata matters
- Whether Supabase Fullstack is available for local review guidance
- Whether the answer is based on live project evidence, local repo evidence, or both

## Source Material

The plugin vendors the useful references and scripts from the prior two plugins so it remains standalone after the old plugin sources are removed.
When the Supabase App connector is available in the current environment, these skills should use it for direct database, functions, branching, and storage operations while keeping the skill guidance focused on correctness, safety, and performance.

## Packaging Notes

The bundled Postgres and Supabase reference corpus is intentionally kept in-tree even though it produces a high deferred token budget in `plugin-eval`.
After the manifest cleanup, skill-description rewrite, and contributor-doc removal pass, the source bundle re-evaluated at `77/100` with only the deferred budget failure remaining.
That remaining cost is currently accepted as the tradeoff for a self-contained standalone plugin that keeps detailed references available without depending on an external docs fetch path.
