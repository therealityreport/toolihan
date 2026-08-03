# Environment Diff

Use when behavior differs across local, CI, staging, production, profiles,
machines, shells, branches, or app bundles.

## Diff Surfaces

- Code: branch, commit, generated files, build artifacts, package cache.
- Runtime: interpreter, Node/Python/Swift/JDK version, PATH, shell, process manager.
- Config: env vars, flags, secrets presence, profiles, app settings.
- Data: database row, tenant, fixture, cache, local storage, migration state.
- Platform: OS, architecture, browser/profile, runner image, permissions.
- Network: endpoint, proxy, DNS, region, rate limits, dependency status.

## Method

1. Pick the smallest failing environment pair.
2. List only differences that can affect the failing surface.
3. Change or simulate one variable at a time when safe.
4. Preserve the before/after signal.

## Stop Conditions

- Sensitive values are required and cannot be redacted.
- Differences are too broad to test one at a time.
- Matching environments would require destructive changes.
