---
name: check-tool-updates
description: Run or schedule Tool Finder's daily update report for watched projects, including Git repos, npm packages, Python packages, Homebrew Brewfiles, and MCP package references.
---

# Check Tool Updates

Use this skill when the user asks whether tools, repos, packages, MCPs, brews, or Python packages need updates across projects.

Use the marketplace diff when the request is specifically about OpenAI plugin availability, registry/app-directory differences, local plugin cache drift, or plugins present in one source but missing from another:

```bash
python3 scripts/marketplace_diff.py --openai-repo /path/to/openai-plugins --format json
```

The diff is read-only and can also write `--markdown-out` and `--html-out` summaries for automation reports. See `docs/marketplace-diff.md`.

## One-Time Check

Run:

```bash
python3 scripts/check_updates_daily.py --report-dir ~/.agents/tool-finder/reports
```

Add `--notify` when the user wants a macOS notification after the report is written.

## Daily Automation

Install or refresh the daily user-level launchd job:

```bash
python3 scripts/install_daily_update_check.py --load
```

Defaults:

- Runs once per day at 9:00 local time.
- Writes reports to `~/.agents/tool-finder/reports`.
- Writes logs to `~/.agents/tool-finder/logs`.
- Uses config at `~/.agents/tool-finder/update-watch-config.json`.
- Shows a macOS notification with the summary.

## Safety

The automation reports only. It does not run updates:

- No `git pull`.
- No `npm update`.
- No `python -m pip install`.
- No `pipx upgrade`.
- No `brew upgrade`.

Report suggested commands as inspection or dry-run actions unless the user separately asks to execute updates.
