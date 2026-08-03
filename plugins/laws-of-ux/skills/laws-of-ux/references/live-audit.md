# Live audit — the optional `--url` pass

The static audit grades from source. About nine laws need rendered geometry, real timings, or
pixels to judge honestly. When the user passes `--url <addr>` (a running dev server or deployed
URL), `/ux-audit` runs a live pass that **upgrades** those laws from `NOT_ASSESSED` / floor-only
to measured, and sets their confidence `c` to 1.0. Live measurement **wins** over static
inference for the laws it covers; the report labels each law's basis (`static` vs `live`).

The live pass reuses the **already-installed `chrome-devtools` MCP** (no server is bundled). It
is opt-in because it needs a reachable running app, drives a real browser (side effects, auth
walls), and is slower/rate-limited. Tool names may be namespaced (e.g.
`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` or `mcp__chrome-devtools-codex-shared__*`);
load them with ToolSearch (`query: "chrome-devtools"`) if deferred. If no chrome-devtools MCP is
connected, skip the live pass and say so — keep the static grade.

## Law → tool mapping

| Law | How to measure live | Tool(s) |
|---|---|---|
| **Doherty Threshold** | Real LCP / INP / TBT and API response times; grade against the ~400ms / Core Web Vitals thresholds instead of "a spinner exists". | `lighthouse_audit`; `performance_start_trace` / `performance_stop_trace` / `performance_analyze_insight`; `list_network_requests` |
| **Fitts's Law** | Real rendered hit areas + spacing of adjacent safe/destructive actions via `getBoundingClientRect()` on every interactive element — replaces the unreliable CSS floor-check. | `take_snapshot` + `evaluate_script` |
| **Aesthetic-Usability, Prägnanz** | Visual judgment on rendered pixels at desktop **and** mobile viewports. | `take_screenshot`, `resize_page` / `emulate` |
| **Gestalt (Proximity, Common Region, Uniform Connectedness, Similarity)** | Actual visual grouping + computed spacing/coords, not inferred from class names. | `take_screenshot` + `evaluate_script` |
| **Selective Attention** | What is actually visually dominant vs buried; real banner-blindness regions. | `take_screenshot` + layout coords |
| **Von Restorff** | Computed styles of all buttons — does exactly one element actually stand out by contrast/size (measured, not guessed). | `evaluate_script` |
| **Hick's / Choice Overload** | Counts of *actually visible* interactive elements (excludes hidden/conditional branches that inflate source counts). | `take_snapshot` |
| **Occam's / Cognitive Load** | Density from the live DOM + screenshot. | `take_screenshot` + `evaluate_script` |
| **Peak-End / Flow / Goal-Gradient** | Only by *driving* the flow (click/fill through checkout/onboarding) and screenshotting each step — expensive & fragile; treat as an opt-in deep mode, not default. | `click`, `fill`, `take_screenshot` |

## Procedure

1. `new_page` / `navigate_page` to the URL. Confirm it loaded (`take_snapshot`); if it needs
   auth or errors, report and fall back to the static grade.
2. Run `lighthouse_audit` + a performance trace for **Doherty**; record LCP/INP.
3. `evaluate_script` `getBoundingClientRect()` over interactive elements for **Fitts's** and
   computed button styles for **Von Restorff**.
4. `take_screenshot` at desktop and a mobile viewport for **Aesthetic-Usability / Prägnanz /
   Gestalt / Selective Attention**; judge from the images.
5. Feed results into scoring: set `c = 1.0` for each live-measured law, override its static
   ordinal with the measured one, and label the finding basis `live`.

## Static vs live disagreement

The live pass measures the *running build*; static measures the *source*. They can disagree
(source has no skeleton but the framework injects one; a Tailwind class resolves differently at
runtime). **Live wins** for the laws it covers, and the report notes the basis so the user sees
why.
