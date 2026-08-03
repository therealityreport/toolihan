# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's security advisory feature for this repository. Do not open a public issue containing credentials, private URLs, session data, personal information, or an exploit that has not been remediated.

## Repository rules

- Never commit API keys, access tokens, cookies, private keys, browser profiles, `.env` files, local databases, raw logs, or runtime caches.
- Use environment-variable placeholders in examples.
- Redact authentication headers, signed URLs, cookies, proxy credentials, and customer data from fixtures and bug reports.
- Treat MCP servers and external CLIs as separate trust boundaries.
- Keep live actions user-authorized and provider-compliant.
