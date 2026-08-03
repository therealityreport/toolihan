# Contributing

Contributions are welcome for fixes, portability improvements, documentation, tests, and new first-party plugins.

## Requirements

1. Put each plugin in `plugins/<plugin-name>`.
2. Include `.codex-plugin/plugin.json`; add `.claude-plugin/plugin.json` only when Claude Code compatibility is tested.
3. Use portable paths and environment variables. Do not include machine-specific absolute paths.
4. Add licensing and upstream attribution.
5. Do not commit generated output, dependency folders, caches, credentials, sessions, or private project material.
6. Regenerate and validate the catalog:

```bash
npm run catalog
npm test
```

Marketplace entries must use relative `./plugins/<plugin-name>` paths and keep plugin names aligned with folder and manifest names.
