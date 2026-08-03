# Browser Runtime Proof

Use when the bug appears through localhost, a browser UI, rendered state,
network calls, profile state, or console/runtime errors.

## Evidence To Capture

- URL, route, viewport, browser/profile name, and exact user action.
- Screenshot or visible-state description tied to the symptom.
- Console errors, network failures, response codes, and relevant request payloads.
- App/server logs for the same timestamp or request ID.
- Source/runtime parity when the browser may be serving stale assets.

## First Probes

- Load the target route and preserve the visible failing state.
- Check console and network before changing code.
- Confirm the dev server, build output, and browser cache/profile being used.
- Compare expected data source with rendered data.

## Stop Conditions

- Browser automation fails twice with the same bridge error.
- The visible failure depends on credentials or private profile state not available.
- The route cannot be served or the running app copy is unknown.

## Handoff Line

`Browser proof: route=<url>, profile=<name>, visible=<state>, console=<summary>, network=<summary>.`
