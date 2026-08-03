# Daily Update Check

Tool Finder can scan watched projects once per day and report update candidates across:

- Git repositories with configured upstream branches.
- npm dependencies via `npm outdated --json --long`.
- pinned Python requirements in `requirements*.txt` and `pyproject.toml`.
- Homebrew `Brewfile` entries via `brew outdated --json=v2`.
- MCP configs that reference npm, `uvx`, or `pipx` packages.

The checker does not update anything. It writes reports and, when enabled, shows a macOS notification.

## Install The Automation

From the plugin root:

```bash
python3 scripts/install_daily_update_check.py --load
```

Defaults:

- schedule: daily at 9:00 local time
- launchd label: `com.thomashulihan.tool-finder.daily-update-check`
- config: `~/.agents/tool-finder/update-watch-config.json`
- reports: `~/.agents/tool-finder/reports`
- logs: `~/.agents/tool-finder/logs`

Change the schedule:

```bash
python3 scripts/install_daily_update_check.py --hour 8 --minute 30 --load
```

Run a one-time check:

```bash
python3 scripts/check_updates_daily.py --config ~/.agents/tool-finder/update-watch-config.json --report-dir ~/.agents/tool-finder/reports --notify
```

## Config

Default config:

```json
{
  "roots": [
    "~/Projects",
    "~/Documents/Codex",
    "~/.agents/plugins/plugins",
    "~/.codex/plugins"
  ],
  "maxDepth": 4,
  "maxProjects": 250,
  "checks": {
    "git": true,
    "npm": true,
    "python": true,
    "homebrew": true,
    "mcp": true
  }
}
```

## Report Shape

Each run writes:

- `update-check-YYYY-MM-DD.json`
- `update-check-YYYY-MM-DD.md`
- `latest.json`
- `latest.md`

Findings use these severities:

- `update`: a newer version or remote state appears available.
- `warning`: the checker could not inspect a source.
- `notice`: a non-blocking condition, such as an unpinned MCP package.

## Boundaries

The checker is intentionally conservative:

- Git checks compare local `HEAD` with the upstream branch SHA from `git ls-remote`; it does not fetch or pull.
- npm checks rely on `npm outdated`.
- Python checks only compare exact pins such as `package==1.2.3`.
- Homebrew checks only reports outdated items that are present in a project `Brewfile`.
- MCP checks report unpinned packages and pinned npm/Python package updates when metadata is available.
