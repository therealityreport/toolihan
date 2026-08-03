# Capability Integrations

This file is kept for older links. Use `capability-router.md` as the canonical
capability map for tools, MCPs, connectors, plugins, CLIs, agents,
availability labels, fallbacks, and stop conditions.

Tool Finder is a maintenance and discovery aid, not a default debugging probe.
For ordinary failures, route by the symptom first and do not list Tool Finder
unless discovery is explicitly part of the request. If discovery is secondary,
label Tool Finder as `[optional]` and keep direct evidence as the primary path.

Expected labels:

| Label | Meaning |
| --- | --- |
| `[available]` | Callable, installed, exposed, or present. |
| `[optional]` | Helpful but not required for the first evidence loop. |
| `[unavailable]` | Missing or not exposed; use the fallback. |
| `[blocked]` | Present but missing credentials, access, profile state, or safe ownership. |
