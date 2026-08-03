# Tool Finder Provider Dependencies

Tool Finder separates provider implementation from provider availability.

## Provider Source Labels

Each normalized result includes `providerSource`:

- `direct-api`: Tool Finder calls a public provider API itself.
- `connector-plugin`: Tool Finder found a callable plugin connector in a supplied runtime catalog.
- `package-registry`: Tool Finder queried a package registry such as npm, PyPI/Python, or Homebrew.
- `runtime-catalog`: Tool Finder found a generic callable runtime tool in a supplied catalog.
- `local-filesystem`: Tool Finder found local skills, plugins, MCP configs, scripts, or package metadata.

## GitHub

Tool Finder has two GitHub paths:

- Direct API provider: `scripts/search_github.py` calls the GitHub REST search API.
- Plugin connector support: `scripts/search_runtime_tools.py` recognizes GitHub connector tools from a runtime connector catalog and labels those results `providerSource: connector-plugin`.

Direct API search does not depend on the `@github` plugin. It uses unauthenticated repository search when possible and `GITHUB_TOKEN` or `gh auth token` for code search. The all-provider command uses GitHub CLI auth by default when `GITHUB_TOKEN` is not set; pass `--no-gh-token` to disable that fallback.

## Hugging Face

Tool Finder has two Hugging Face paths:

- Direct API provider: `scripts/search_huggingface.py` calls public Hugging Face Hub API endpoints for models, datasets, and Spaces.
- Plugin connector support: `scripts/search_runtime_tools.py` recognizes Hugging Face connector tools from a runtime connector catalog and labels those results `providerSource: connector-plugin`.

Direct API search does not depend on the `@hugging-face` plugin. `HF_TOKEN` is optional for public Hub resources and can be supplied for authenticated Hub access.

## Runtime Connector Catalogs

Plain shell scripts cannot inspect live Codex MCP tools by themselves. Use:

```bash
python3 scripts/export_runtime_connector_catalog.py --template
```

Fill the template with callable tool metadata from the current assistant session, then pass it to:

```bash
python3 scripts/search_all_providers.py "<query>" --runtime-catalog runtime-connectors.json
```

This lets Tool Finder show installed plugin connectors beside direct API and registry results without pretending those connector APIs are available to standalone Python.

## Tool Report Exports

Tool Finder can turn an all-provider payload into a readable report bundle:

```bash
python3 scripts/search_all_providers.py "<query>" --root "$PWD" --report-dir ./tool-finder-report
```

The report bundle includes:

- `TOOLS.md`, the required implementation shortlist for tools, repositories, models, packages, scripts, connectors, or features to consider implementing fully, integrating partially, borrowing, or keeping as reference only.
- `TOOLS.html`, grouped by suggested tool type such as MCP, CLI, CONNECTORS, SKILLS, AGENTS, PLUGINS, MODELS, PACKAGES, DATASETS, APPS / SPACES, HOOKS / SCRIPTS, TOOL SCHEMAS, and OTHER.
- `sources/*.html`, one media-rich HTML page for each source represented by provider results or provider status.
- `types/*.html`, one media-rich HTML page for each suggested tool type represented by results.
- `source-types/<source>/<type>.html`, one media-rich HTML page for each source/type pair that returned results.
- Source favicons, source links, type/source cross-links, status cards, and result cards for website-backed providers such as Hugging Face, GitHub, skills.sh, npm, PyPI/Python, and Homebrew.

Report export is a presentation layer. It does not change provider availability, install tools, fetch remote code, or store provider tokens.
