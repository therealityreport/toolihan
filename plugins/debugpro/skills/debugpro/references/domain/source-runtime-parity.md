# Source Runtime Parity

Use when the edited source, packaged artifact, installed copy, cache, or running
process may not be the same thing.

## Evidence To Capture

- Source path, package path, installed/runtime path, and cache path.
- Process command, working directory, loaded config, version, and build timestamp.
- Manifest, lockfile, generated artifact, and symlink resolution.
- Diff between source and runtime copies for the failing surface.
- Proof of which copy changed after rebuild, reinstall, or refresh.

## Common Causes

- Editing a repo copy while the app runs a packaged or cached copy.
- Stale build output, extension bundle, serverless deploy, plugin cache, or app bundle.
- Symlink, wrapper, PATH, profile, environment, or service manager selecting another copy.
- Runtime refresh script regenerating files from a different template.

## Stop Conditions

- Runtime path cannot be identified.
- Rebuild or reinstall would mutate shared state without approval.
- Another worker owns the target runtime or cache file.

## Handoff Line

`Source/runtime parity: source=<path>, runtime=<path>, cache=<path>, process=<pid/cmd>, diff=<summary>.`
