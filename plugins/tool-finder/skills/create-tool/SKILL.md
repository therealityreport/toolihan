---
name: create-tool
description: Create a new skill, plugin, MCP config, CLI wrapper, hook, or agent asset only after existing matches are weak or unsafe.
---

# Create Tool

Create new tooling only when discovery does not find a strong match.

Creation priority:

1. Skill for focused instructions.
2. Plugin for packaged skills, scripts, assets, apps, or MCP config.
3. MCP config only when an actual server exists.
4. CLI wrapper only when command behavior is concrete.
5. Hook only when lifecycle trigger and rollback behavior are clear.

Use the templates under `assets/templates/` when creating new assets. Validate frontmatter, plugin manifests, JSON config, and script syntax before handoff.
