# Frontend Debugging

Use when the symptom involves rendering, hydration, state, forms, routing,
browser data flow, assets, or client/server boundaries.

## Evidence To Capture

- Route, viewport, component surface, user action, and expected visible result.
- Console errors, network requests, response payloads, cache behavior, and source maps.
- State source: props, store, query cache, URL params, local storage, cookies, or server data.
- Build mode, dev server, bundle path, and hydration/client boundary.
- Screenshot or DOM evidence tied to the failure.

## First Probes

- Reproduce the visible state before editing.
- Trace data from source to rendered output.
- Separate CSS/layout, component state, network/API, hydration, and stale asset causes.
- Check mobile and desktop constraints only when layout is part of the symptom.

## Stop Conditions

- The app cannot be served or the running bundle is unknown.
- Auth/profile state is required and unavailable.
- Browser proof cannot be captured and logs do not identify the failing surface.

## Handoff Line

`Frontend proof: route=<url>, component=<name>, state_source=<source>, visible=<summary>, console/network=<summary>.`
