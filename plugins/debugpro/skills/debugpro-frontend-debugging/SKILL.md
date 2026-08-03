---
name: debugpro-frontend-debugging
description: Use when frontend rendering, routing, hydration, state, assets, or browser behavior fails.
---

# DebugPro Frontend Debugging

Use this route to connect visible UI behavior to the frontend code and runtime state that caused it.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/frontend-debugging.md`

## When To Use

- The symptom is a broken UI state, wrong content, bad interaction, missing route, hydration issue, layout problem, or client error.
- The failure appears only after browser navigation, client state changes, API responses, or asset loading.
- A fix must preserve existing component, design-system, routing, and state-management patterns.

## Evidence To Collect

- URL, viewport, user flow, visible state, expected state, and screenshot.
- Console errors, network calls, API payload shape, route params, and client state inputs.
- Component path, data owner, routing layer, style source, and loaded bundle/build id.
- Relevant accessibility, responsive, and loading/error states when they affect the symptom.
- Prior and current behavior if a regression window is known.

## First Probes

- Reproduce in browser and capture screenshot, console, network, and DOM state.
- Trace from visible UI to route, component, data fetch, state update, and style source.
- Check whether the bug is data, routing, render logic, state lifetime, cache, CSS, or asset loading.
- Use the smallest local test or focused runtime probe that exercises the failing component path.
- Verify fixes in the original browser flow and viewport.

## Optional Tools, MCPs, And Connectors

- Browser, Chrome, Chrome DevTools MCP, or Playwright MCP for runtime UI proof.
- Framework CLIs and logs for route compilation, hydration, bundling, and type errors.
- Design-system docs or component references when existing UI conventions control the fix.
- Context7 or official docs when current framework, library, or CLI behavior is uncertain.

## Route-Specific Fallbacks

- If browser access fails, use server responses, compiled route output, static render evidence, logs, and code tracing.
- If backend data is unavailable, fixture the observed payload shape or mark the missing data boundary before changing UI logic.
- If design intent is missing, keep the fix minimal and consistent with nearby components.

## Route-Specific Stop Conditions

- The next step would invent product behavior, change shared design patterns, or rewrite state architecture without approval.
- The symptom depends on missing credentials, inaccessible data, or an unknown runtime owner.
- A proposed fix cannot be verified against the original visible flow.

## Output Format

```markdown
## Frontend Debug Report
- Visible symptom:
- URL/viewport/flow:
- Runtime evidence:
- Console/network evidence:
- Component/data owner:
- Cause:
- Fix:
- UI verification:
- Accessibility/responsive impact:
- Stop condition or residual risk:
```
