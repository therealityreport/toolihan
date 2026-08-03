---
name: self-check-tool-finder
description: Check Tool Finder provider health and report which local, live, auth-gated, skipped, or deferred providers are available.
---

# Self-Check Tool Finder

Check whether Tool Finder can reach its providers without installing or modifying tools.

Run:

```bash
python3 scripts/self_check_providers.py
```

Use `--runtime-catalog <path>` when a callable Codex tool catalog JSON file is available. Without that file, runtime catalog lookup is reported as skipped because shell scripts cannot see the assistant's live tool catalog directly.

Report:

- Overall status: `ok`, `partial`, or `degraded`.
- Provider checks with searched/skipped/error/deferred state.
- Auth requirements and remediation for skipped providers.
- Result counts from the same provider path used by `scripts/search_all_providers.py`.

Do not execute installs, package updates, or remote writes during self-check.
