---
name: github-code-auth
description: Diagnose GitHub code-search auth for Tool Finder without printing or storing tokens.
---

# GitHub Code Auth

Use this when Tool Finder skips GitHub code search because both `GITHUB_TOKEN` and GitHub CLI auth are unavailable, or when the user wants to diagnose GitHub auth before a search.

Run:

```bash
python3 scripts/github_code_auth_helper.py --token-env GITHUB_TOKEN --use-gh-token
```

Report:

- Whether the token environment variable is present.
- Whether GitHub CLI is installed and appears authenticated.
- Whether GitHub CLI can provide an ephemeral token for Tool Finder child processes.
- The concrete next command to enable Tool Finder code search.

Do not print tokens, write tokens to files, or execute remote GitHub writes. The `--use-gh-token` option confirms that `gh auth token` can be used by Tool Finder without exposing the token value.
