---
name: debugpro-browser-runtime-proof
description: Use when a browser, localhost, UI, or web runtime failure needs direct runtime evidence before diagnosis or verification.
---

# DebugPro Browser Runtime Proof

Use this route to capture what the browser actually renders, requests, logs, and executes.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/browser-runtime-proof.md`

## When To Use

- A localhost, web app, extension, UI route, or browser-only symptom must be reproduced.
- A source change needs visible proof in the running browser.
- The failure depends on cookies, profile state, service workers, network requests, console errors, routing, hydration, or loaded assets.

## Evidence To Collect

- URL, browser/profile name, viewport, repro steps, expected behavior, and actual behavior.
- Screenshot or DOM proof of the visible state.
- Console errors, failed requests, response codes, headers, and relevant payload snippets.
- Server logs, dev-server output, build id, loaded asset URLs, and source/runtime path mapping.
- Whether refresh, hard refresh, profile switch, or server restart changes the symptom.

## First Probes

- Open the exact URL and reproduce the symptom with the Browser plugin, Chrome, or another available runtime surface.
- Capture screenshot, console, network failures, and current DOM state.
- Check server health with `curl`, dev-server logs, and route-specific requests.
- Check cache and runtime boundaries: service worker, asset hash, build output, and active process.
- Verify any fix in the same browser route where the symptom was observed.

## Optional Tools, MCPs, And Connectors

- Browser plugin for localhost navigation, screenshots, and interaction proof.
- Chrome or Chrome DevTools MCP when existing profile state, extensions, cookies, or DevTools detail matters.
- Playwright MCP or local Playwright when repeatable browser probes are useful.
- `curl`, app logs, framework devtools, and source maps for request/runtime evidence.

## Route-Specific Fallbacks

- If browser automation is unavailable, use `curl`, server logs, static screenshots if available, and source/runtime asset checks.
- If the profile cannot be accessed, state the missing profile and reproduce in the closest available browser while marking profile-specific risk.
- If the UI cannot be opened, prove the nearest boundary: server response, route compile, bundle generation, or network error.

## Route-Specific Stop Conditions

- The next probe requires credentials, destructive cache clearing, profile mutation, or production interaction without approval.
- The visible state conflicts with source evidence and the active runtime path is not identified.
- Required server, route, profile, or app process is unavailable.

## Output Format

```markdown
## Browser Runtime Proof Report
- URL/profile:
- Repro steps:
- Expected:
- Actual:
- Screenshot/DOM proof:
- Console/network evidence:
- Server/runtime evidence:
- Source/runtime boundary:
- Cause:
- Fix:
- Browser verification:
- Stop condition or residual risk:
```
