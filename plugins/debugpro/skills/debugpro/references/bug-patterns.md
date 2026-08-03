# Bug Pattern Catalog

Use as a checklist for hypotheses, not as proof.

| Pattern | Evidence that supports it |
| --- | --- |
| Stale runtime artifact | Source differs from running bundle, cache, installed copy, or process path. |
| Wrong environment | Interpreter/runtime, PATH, profile, branch, env vars, or config differs. |
| Boundary mismatch | API/schema/auth assumptions differ across caller and callee. |
| Race or timing | Repeat count, logs, traces, or ordering changes the result. |
| State pollution | Earlier test/action changes shared data, cache, singleton, filesystem, or browser storage. |
| Data cohort issue | Failure only appears for specific tenant, row, payload, or migration state. |
| Dependency drift | Lockfile, package version, release notes, or transitive change aligns with failure. |
| Permission/auth issue | Token, role, entitlement, profile, secret, or scope differs from expected. |
| Resource pressure | CPU, memory, disk, connection pool, queue depth, or rate limit aligns with failure. |
| UI layout/state issue | DOM, CSS, viewport, hydration, store, or query cache differs from expectation. |

## Rule

Every pattern needs a falsifying probe. If no probe is available, label it as a
guess and return to evidence collection.
