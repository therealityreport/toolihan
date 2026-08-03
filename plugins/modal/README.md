# Modal

User-level Codex plugin for Modal architecture, implementation, deployment, and operations guidance.

The plugin root is:

```text
plugins/modal
```

The plugin bundles the `$modal-platform` compatibility skill under `skills/modal-platform/`.

The plugin display name is `Modal`; the skill name remains `$modal-platform` for compatibility with existing prompts and wrappers.

Refresh exact Modal behavior from official docs when syntax, limits, or current CLI behavior matters:

- https://modal.com/llms.txt
- https://modal.com/llms-full.txt
- https://modal.com/docs/guide
- https://modal.com/docs/examples
- https://modal.com/docs/reference

## Docs Indexes

Use the checked-in indexes for quick routing, then open official docs for exact syntax:

- API and SDK: `skills/modal-platform/references/modal-api-index.md`
- CLI commands: `skills/modal-platform/references/modal-cli-index.md`
- Guides: `skills/modal-platform/references/modal-guide-index.md`

The CLI index covers the current `https://modal.com/docs/cli/latest/...` command reference, including `modal app`, `billing`, `bootstrap`, `changelog`, `config`, `container`, `curl`, `dashboard`, `deploy`, `dict`, `endpoint`, `environment`, `image`, `profile`, `queue`, `run`, `secret`, `serve`, `setup`, `shell`, `skills`, `token`, `volume`, and `workspace`.

This public package intentionally excludes private project-specific Modal MCP launchers and credentials. Use Modal's official CLI and authentication flow for live operations.
