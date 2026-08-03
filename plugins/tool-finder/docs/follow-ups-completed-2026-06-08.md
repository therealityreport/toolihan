# Follow-ups Completed - 2026-06-08

Completed follow-up scope:

- Installed Tool Finder into the personal plugin marketplace.
- Added live npm registry discovery through `scripts/search_npm.py`.
- Added live PyPI project metadata discovery through `scripts/search_pypi.py`.
- Connected `scripts/search_github.py` to live GitHub REST repository and code search with `--live`.
- Added a static result comparison UI at `assets/comparison-ui/index.html`.
- Added confirmed install execution design at `docs/confirmed-install-execution.md`.
- Added live Homebrew formula/cask discovery through `scripts/search_homebrew.py`.
- Added live pips install planning through `scripts/search_pips.py`.
- Added unified Python provider through `scripts/search_python.py`.
- Added daily update reporting through `scripts/check_updates_daily.py`.
- Added launchd installer through `scripts/install_daily_update_check.py`.

Marketplace install:

- Marketplace: `<marketplace-root>/.agents/plugins/marketplace.json`
- Installed plugin path: `<marketplace-root>/plugins/tool-finder`
- Marketplace source path: `./plugins/tool-finder`

Validation performed:

- `PYTHONDONTWRITEBYTECODE=1 python3 <codex-skill-root>/plugin-creator/scripts/validate_plugin.py outputs/tool-finder`
- `PYTHONDONTWRITEBYTECODE=1 python3 <codex-skill-root>/plugin-creator/scripts/validate_plugin.py <marketplace-root>/plugins/tool-finder`
- `PYTHONPYCACHEPREFIX=/tmp/tool-finder-pycache python3 -m py_compile outputs/tool-finder/scripts/*.py`
- `python3 outputs/tool-finder/scripts/search_npm.py detail yargs`
- `python3 outputs/tool-finder/scripts/search_pypi.py detail black`
- `python3 outputs/tool-finder/scripts/search_github.py "model context protocol server" --live --type repositories --limit 1`
- `python3 outputs/tool-finder/scripts/search_homebrew.py detail wget --kind formula`
- `python3 outputs/tool-finder/scripts/search_pips.py detail black --installer auto`
- `python3 outputs/tool-finder/scripts/search_python.py detail black --installer auto`
- `python3 outputs/tool-finder/scripts/check_updates_daily.py --config /tmp/tool-finder-test-config.json --report-dir /tmp/tool-finder-reports`
- JavaScript syntax check for `assets/comparison-ui/index.html`.

Provider behavior:

- npm uses the public npm registry package metadata and search endpoints.
- PyPI uses the official project JSON endpoint, so search mode resolves exact project-name candidates instead of pretending there is an official free-text JSON search API.
- GitHub live search is read-only and treats code results and repository results as reference material.
- Homebrew uses the official formulae.brew.sh formula/cask JSON API.
- Python uses a unified provider view that combines PyPI metadata with pip/pipx install-plan commands.
- The daily update checker writes reports and optional notifications; it does not execute updates.
- All install outputs remain dry-run plans.
