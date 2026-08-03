---
name: find-similar-usage
description: Find repositories that use a named tool in a similar way to the user's intended workflow.
---

# Find Similar Usage

Find real repositories that use a named tool in a similar way.

Use `scripts/find_similar_usage.py` to produce GitHub query plans.

Prefer evidence from:

- Config files.
- Imports.
- Command invocations.
- MCP server setup.
- Plugin manifests.
- Skill files.
- Agent instruction files.

Avoid treating README-only mentions as strong evidence unless no better examples exist. Similar repositories are examples and evidence, not direct install recommendations.
