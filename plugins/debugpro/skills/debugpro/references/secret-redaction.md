# Secret Redaction

Use this before sharing logs, traces, environment dumps, proxy output, MCP diagnostics, API errors, or browser/session artifacts.

## Always Redact

- API keys, bearer tokens, auth headers, cookies, session ids, refresh tokens, OAuth codes, OTPs, passwords, SSH keys, private keys, and proxy credentials.
- `.env` values, launchctl environment values, CI secrets, connection strings, database URLs, signed URLs, and webhook secrets.
- Direct personal contact, payment, medical, financial, precise-location, or account identifiers unless the user explicitly asked to transmit them to a specific destination.

## Preserve For Debugging

- Error code, status code, endpoint host, sanitized path, timestamp, request id, trace id, release, environment, service, and non-secret config key names.
- Token state as categories: missing, malformed, present-but-untested, tested-ok, expired, wrong-scope, wrong-project, or unavailable.

## Rules

- Never paste raw secrets into reports or generated artifacts.
- If redaction would remove the only evidence, state the missing evidence and ask for a sanitized reproduction or log excerpt.
- When classifying auth or quota failures, prefer concrete redacted error fields over guesses.
