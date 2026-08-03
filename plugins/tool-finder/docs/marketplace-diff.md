# Marketplace Diff

Use `scripts/marketplace_diff.py` when Codex needs to compare OpenAI plugin availability against local app and plugin state.

The command reads local files only. It does not install, remove, update, fetch, or mutate plugin caches.

## Sources

- `openai/plugins` checkout, usually passed with `--openai-repo`.
- `~/.codex/cache/codex_app_directory`.
- `~/.codex/plugins/cache/openai-*`.
- `~/.codex/plugins/cache/local-plugins`.
- top-level `~/.codex/plugins`.

## Example

```bash
python3 scripts/marketplace_diff.py \
  --openai-repo /path/to/openai-plugins \
  --json-out marketplace-diff.json \
  --markdown-out marketplace-diff.md \
  --html-out marketplace-diff.html
```

## Output

The JSON report uses `tool-finder.marketplace-diff.v1` and includes:

- `new`: entries present in `openai/plugins` but not in the app directory or OpenAI plugin cache.
- `removed`: app-directory or cache entries that are not present in the OpenAI repo snapshot.
- `updated`: matching entries whose visible versions differ across sources.
- `missing`: OpenAI repo entries missing from the app directory or OpenAI cache.
- `cacheDrift`: differences between editable local plugins and local cache copies.

Use the Markdown or HTML output for compact automation reports.
