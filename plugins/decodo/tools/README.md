# Decodo Tool Helpers

This folder stores helper code for Decodo scripts and skills. It is not an
auto-exposed Codex tool surface.

## Folders

- `decodo-sdk-runner/` provides SDK/auth helper functions used by
  `scripts/doctor-decodo-auth.mjs` and `scripts/smoke-decodo-sdk.mjs`.
- `decodo-proxy-checks/` provides proxy validation and opt-in live probe helper
  functions used by `scripts/doctor-decodo-proxies.mjs` and
  `scripts/smoke-proxy-rotation.mjs`.
- `decodo-fixtures/` provides shared redaction, CLI helpers, and generated
  redaction fixtures used by all wrappers.

## Safety Rules

- Helpers do not make live network calls unless a script passes explicit live
  options.
- Helpers must not print raw tokens, usernames, passwords, authorization header
  values, `.env` values, or proxy URLs with embedded credentials.
- Amazon, ecommerce, and purchase automation workflows are intentionally out of
  scope for these helpers.
