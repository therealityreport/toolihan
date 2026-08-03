# Capability Map

Use this map when planning or validating MCP Apps, ChatGPT Apps, Apps SDK projects, or local Codex plugin/app surfaces.

## Primary Sources

- OpenAI Developers docs are the first source for Apps SDK behavior, ChatGPT UI resources, MCP server wiring, app submission, and Codex config docs.
- MCP Apps docs are the first source for bridge behavior, resource metadata, and MCP App extension terms when they are more specific than general Apps SDK docs.
- Official upstream examples are preferred when a requested app closely matches an existing example.

## Local Capabilities

- Context7 is a fallback for current external library, package, framework, SDK, CLI, or cloud-service docs when official OpenAI docs are not the owner.
- Tool Finder is for local tool/plugin/skill inventory and candidate discovery before deciding what to wrap.
- Plan Architect is for substantial plugin plans, handoffs, and validation ledgers.
- Plugin Creator validator checks plugin packaging after source edits.
- Node `--check` validates dependency-free script syntax.

## Defaults

- Do not install new packages by default.
- Do not add persistent agents, React generation, submission automation, auth, storage, or deployment unless the user asks for that stage.
- Keep generated starters small, inspectable, and aligned with the existing archetype table.
