---
name: find-alternatives
description: Find alternatives to a named tool, connector, MCP server, skill, plugin, agent, CLI, hook, or package.
---

# Find Alternatives

Find alternatives when the user names an existing tool or asks what else could solve the same job.

Use `scripts/find_alternatives.py` to generate search plans and comparison categories.

For each alternative:

- Explain what it replaces.
- Explain what it does better.
- Explain what the original still does better.
- Show install/auth complexity.
- Show safety and maintenance signals.

Do not recommend replacement automatically. Present alternatives as choices.
