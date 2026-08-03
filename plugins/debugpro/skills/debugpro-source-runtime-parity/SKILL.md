---
name: debugpro-source-runtime-parity
description: Use when source files, packaged files, installed runtime files, caches, generated output, or live behavior may be out of sync.
---

# DebugPro Source Runtime Parity

Use this route to prove whether the code being edited is the code being executed.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/source-runtime-parity.md`

## When To Use

- A fix exists in source but the live app, CLI, plugin, cache, or package still behaves differently.
- A runtime cache, installed app, generated bundle, symlink, build output, or packaged default may be stale.
- Multiple source roots, checkout links, app support folders, or versioned caches may own the same visible behavior.

## Evidence To Collect

- Exact symptom, command, UI route, process, or runtime surface that proves the mismatch.
- Source path, runtime path, cache path, installed path, and any symlink resolution.
- File mtimes, checksums, versions, package metadata, manifest values, and build ids.
- Process command line, working directory, environment variables, and loaded config paths.
- Any build, publish, install, reload, or refresh step already attempted.

## First Probes

- Resolve path ownership with `pwd`, `realpath`, `ls -la`, `find`, and `rg`.
- Compare source and runtime copies with `diff -ru`, `cmp`, checksums, and manifest/version reads.
- Inspect process/runtime state with `ps`, `lsof`, app logs, CLI `--version`, and config dumps.
- Reproduce against both source and runtime paths when possible.
- After a fix, verify the original symptom against the runtime surface, not only source tests.

## Optional Tools, MCPs, And Connectors

- Browser or Chrome for visible localhost/runtime proof.
- GitHub or `gh` only when source provenance, branch state, or PR artifacts matter.
- Project-specific CLIs for package, app, plugin, extension, or deployment cache inspection.
- Context7 or official docs when current packaging, cache, or CLI behavior is uncertain.

## Route-Specific Fallbacks

- If a runtime path cannot be inspected, capture the missing permission or unavailable surface and prove the nearest readable boundary.
- If rebuild or reinstall is out of scope, report the exact stale boundary and the command that would refresh it.
- If ownership is ambiguous, stop before editing and return a path map with candidate owners.

## Route-Specific Stop Conditions

- The next step would delete caches, reinstall apps, mutate user config, or change global state without approval.
- Concurrent edits make it unclear which source or runtime copy should win.
- Required runtime access, credentials, or logs are unavailable.

## Output Format

```markdown
## Source Runtime Parity Report
- Symptom:
- Source path:
- Runtime path:
- Cache/installed path:
- Ownership proof:
- Drift found:
- First probes run:
- Cause:
- Fix or refresh needed:
- Runtime verification:
- Stop condition or residual risk:
```
