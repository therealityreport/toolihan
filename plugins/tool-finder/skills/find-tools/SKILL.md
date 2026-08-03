---
name: find-tools
description: Find agents, skills, plugins, MCP servers, connectors, CLIs, hooks, scripts, and tool schemas for a user job. Use when the user asks to find, discover, search for, or choose tooling.
---

# Find Tools

Find the best available tool for the user's job.

## Search Order

Prefer the single all-provider command for broad discovery:

```bash
python3 scripts/search_all_providers.py "<tool or job>" --root "$PWD"
```

This command searches every available provider, keeps partial results when one provider fails, returns `providerStatus` plus `skippedProviders`, and writes `TOOLS.md` by default.

`TOOLS.md` is required for every Tool Finder run. It is the implementation shortlist: tools, repositories, models, packages, scripts, connectors, or specific features to consider implementing fully, integrating partially, or borrowing as reference behavior. If a run truly must avoid filesystem writes, pass `--no-tools-md` and state that exception in the final response.

Tool Finder final-ranks results after all providers return, registry dedupe completes, and provider-source labels are available. Use the `rank`, `rankReason`, `score`, and `bucket` fields when presenting the final list.

Add `--report-dir <dir>` to create a media-rich report bundle in the same run:

- `TOOLS.md`: the required Markdown implementation shortlist with `Fully implement/use`, `Partially integrate`, `Feature to borrow`, and `Reference only` guidance.
- `TOOLS.html`: grouped by suggested tool type, including MCP, CLI, CONNECTORS, SKILLS, AGENTS, PLUGINS, MODELS, PACKAGES, DATASETS, APPS / SPACES, HOOKS / SCRIPTS, TOOL SCHEMAS, and OTHER.
- `sources/*.html`: one source-specific file for providers such as Hugging Face, GitHub Repositories, GitHub Code Search, skills.sh, npm, Python/PyPI, Homebrew, runtime connectors, and local inventory.
- `types/*.html`: one file per suggested tool type, such as MCP, CLI, CONNECTORS, SKILLS, MODELS, and PACKAGES.
- `source-types/<source>/<type>.html`: one file for each source/type pair that returned results.
- Source, type, and source/type pages include provider favicons, provider links, provider status, result counts, rank, score, best action, use path, match reasons, and risk notes.

Example:

```bash
python3 scripts/search_all_providers.py "<tool or job>" --root "$PWD" --report-dir ./tool-finder-report --report-title "Tool Options"
```

For an existing JSON payload, use:

```bash
python3 scripts/export_tool_report.py all-provider-results.json --output-dir ./tool-finder-report --title "Tool Options"
```

This existing-payload export writes both `TOOLS.md` and `TOOLS.html`.

GitHub repository search runs unauthenticated when possible. GitHub code search uses `GITHUB_TOKEN` when set, or GitHub CLI auth through `gh auth token` by default when available; Tool Finder uses that token only for the child GitHub code-search request and does not print or store it. Use `--no-gh-token` to disable the GitHub CLI fallback.

Use `--runtime-catalog <path>` with a catalog produced by `scripts/export_runtime_connector_catalog.py` when the current session has plugin connector tools such as GitHub or Hugging Face. Connector catalog results are labeled `providerSource: connector-plugin`.

Use `--local-limit 0` when the local project inventory is only the baseline and the user wants external tools to add on top of what already exists.

Use `--adoption-scope full`, `--adoption-scope partial`, `--adoption-scope feature`, or `--adoption-scope reference` to filter candidates by adoption depth. The flag is repeatable. Installable tools with commands or install URLs are treated as full or partial implementation candidates, not feature-only references.

It also deduplicates same-name package-manager results across npm, Python/PyPI, and Homebrew. When a duplicate is merged, the primary card keeps alternate package-manager hits in `providerVariants` and `alternatives`. Add configurable aliases with `--dedupe-aliases assets/templates/registry-dedupe-aliases.json` or inline with `--dedupe-alias canonical=alias1,alias2`.

Use individual providers only when the user asks for a narrow source or when debugging one provider:

1. Current callable Codex tools and connectors through the live tool catalog, or `scripts/search_runtime_tools.py` when a runtime catalog JSON file is available.
2. Local installed inventory through `scripts/scan_local_inventory.py`.
3. skills.sh through `scripts/search_skillssh.mjs`. When Vercel OIDC auth is missing, the script returns a structured skipped-provider response instead of failing the whole search.
4. GitHub direct API through `scripts/search_github.py`; use `--live --type repositories` for broad discovery and `--live --type code` for specific implementation patterns. Code search uses `GITHUB_TOKEN` or GitHub CLI auth by default when available. If code search is skipped, run `scripts/github_code_auth_helper.py --use-gh-token` to diagnose token and GitHub CLI setup without printing secrets.
5. Hugging Face direct API through `scripts/search_huggingface.py` for public Hub models, datasets, and Spaces. Use `scripts/huggingface_auth_helper.py --validate-token` when authenticated Hub access is needed.
6. npm, unified Python, and Homebrew through `scripts/search_npm.py`, `scripts/search_python.py`, and `scripts/search_homebrew.py` when the request specifically needs CLIs, MCP servers, apps, packages, or package-manager install paths. Treat `scripts/search_pypi.py` and `scripts/search_pips.py` as compatibility helpers; prefer `scripts/search_python.py` for new Python results.
7. Package registry provider plans through `scripts/plan_package_registries.py` for a provider availability summary.

## Output

Return result cards with:

- Name.
- Asset type.
- Source.
- Provider source, such as direct API, connector plugin, package registry, runtime catalog, or local filesystem.
- Availability.
- Score and bucket.
- Final rank and rank reason.
- Recommended action.
- Match reasons.
- Provider status, including live/local/runtime, skipped, deferred, or error state.
- Risk notes.
- Install or use path.
- Optional report path when `--report-dir` is used.
- `TOOLS.md` path, either `./TOOLS.md`, `<report-dir>/TOOLS.md`, or the explicit `--tools-md` path.

Always show skipped providers with the provider name, reason, auth requirement when relevant, and the next concrete remediation. Do not silently omit a provider that could not run.

When rendering the comparison UI in `assets/comparison-ui/index.html`, pass the full all-provider payload so provider coverage, skipped sources, deduplicated registry variants, and provider/state filters are visible.

Prefer tools that are already callable or locally installed when they solve the job. Do not execute installs. Produce dry-run install or wiring plans only.

Use `scripts/plan_install.py` for an individual normalized result before presenting an install action. Confirmed install execution is not enabled by default; follow the design in `docs/confirmed-install-execution.md` before adding execution.

See `docs/provider-dependencies.md` when explaining whether a result came from a direct Tool Finder API client or from an installed plugin connector.
