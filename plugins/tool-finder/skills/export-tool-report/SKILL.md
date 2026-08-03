---
name: export-tool-report
description: Create a Tool Finder report bundle with the required TOOLS.md shortlist, TOOLS.html, and source/type pages.
---

# Export Tool Report

Create a report bundle when the user wants shareable Tool Finder output, a `TOOLS.md` implementation shortlist, source-specific HTML pages, tool-type HTML pages, provider favicons, or a `TOOLS.html` page grouped by suggested tool type.

## Preferred Flow

Use the all-provider command with `--report-dir` when searching and exporting in one step:

```bash
python3 scripts/search_all_providers.py "<tool or job>" --root "$PWD" --report-dir ./tool-finder-report --report-title "Tool Options"
```

This writes:

- `TOOLS.md`: the required Markdown shortlist of tools, repositories, models, packages, scripts, connectors, and features to consider implementing fully, integrating partially, borrowing, or keeping as reference only.
- `TOOLS.html`: the main index grouped into MCP, CLI, CONNECTORS, SKILLS, AGENTS, PLUGINS, MODELS, PACKAGES, DATASETS, APPS / SPACES, HOOKS / SCRIPTS, TOOL SCHEMAS, and OTHER.
- `sources/*.html`: one HTML page per source, such as Hugging Face, GitHub Repositories, GitHub Code Search, skills.sh, npm, Python/PyPI, Homebrew, runtime connectors, and local inventory.
- `types/*.html`: one HTML page per suggested tool type, such as MCP, CLI, CONNECTORS, SKILLS, MODELS, and PACKAGES.
- `source-types/<source>/<type>.html`: one HTML page for each source/type pair that returned results.

## Existing Payload Flow

If a Tool Finder JSON payload already exists, export it directly:

```bash
python3 scripts/export_tool_report.py all-provider-results.json --output-dir ./tool-finder-report --title "Tool Options"
```

Add `--adoption-scope full`, `--adoption-scope partial`, `--adoption-scope feature`, or `--adoption-scope reference` to export only that adoption depth. Repeat the flag to include multiple depths.

## Report Rules

- Keep report files as standalone HTML.
- Always write `TOOLS.md` and treat it as the implementation decision artifact.
- Include source favicons, source links, provider status, skipped-provider explanations, type/source cross-links, rank, score, best action, use path, match reasons, and risk notes.
- Do not execute installs from the report.
- Use the report as a readable decision artifact; use `scripts/plan_install.py` only after the user selects a specific result.
