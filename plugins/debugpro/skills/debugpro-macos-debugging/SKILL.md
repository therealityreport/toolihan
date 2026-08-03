---
name: debugpro-macos-debugging
description: Use when macOS build, signing, launch, process, logs, or runtime behavior fails.
---

# DebugPro macOS Debugging

Use this route to connect macOS app behavior to build, bundle, signing, launch, process, log, and UI evidence.

Linked references:
- `../debugpro/references/capability-router.md`
- `../debugpro/references/debugging-discipline.md`
- `../debugpro/references/domain/macos-debugging.md`

## When To Use

- A macOS app or helper fails to build, launch, render, sign, notarize, update, quit, or respond.
- The issue depends on installed app bundles, app support files, permissions, launch agents, menu bar state, or desktop UI.
- Source, derived data, installed bundle, and running process may differ.

## Evidence To Collect

- App name, bundle id, installed path, source path, build configuration, and macOS version.
- Exact build, launch, signing, entitlement, permission, crash, or UI symptom.
- `xcodebuild` output, unified logs, crash reports, process state, bundle metadata, and signing details.
- App support/config paths, launch agents, helper tools, environment, and recent installs or updates.
- Screenshot or desktop proof when the failure is visible.

## First Probes

- Confirm source, build product, installed bundle, and running process paths.
- Inspect build or test failure with `xcodebuild`, package manager output, and derived-data context.
- Inspect runtime with `ps`, `lsof`, `log show` or `log stream`, crash logs, and app support files.
- Check bundle metadata, signing, notarization, entitlements, quarantine, and permissions when relevant.
- Verify fixes by rebuilding/relaunching and checking the original app or desktop behavior.

## Optional Tools, MCPs, And Connectors

- Build macOS Apps skills for SwiftUI, AppKit, signing, packaging, build/run/debug, and test triage.
- Computer Use or screenshots when visible desktop state is the primary signal.
- Xcode, `xcodebuild`, `codesign`, `spctl`, `plutil`, `defaults`, and unified logging.
- Context7 or official docs when current SDK, framework, signing, or CLI behavior is uncertain.

## Route-Specific Fallbacks

- If GUI control is unavailable, use screenshots, process/log evidence, and command-line launch checks.
- If signing or entitlement checks require unavailable identity access, report the missing identity and prove bundle metadata boundaries.
- If installed bundle mutation is out of scope, identify the exact source/build/install drift and required refresh step.

## Route-Specific Stop Conditions

- The next step would delete user app data, reset permissions, kill unrelated processes, alter signing identities, or change launch agents without approval.
- Source/build/installed/running ownership is ambiguous.
- Required crash logs, permissions, signing assets, or visible UI access are unavailable.

## Output Format

```markdown
## macOS Debug Report
- App/bundle:
- Symptom:
- Source/build/installed/running paths:
- Build/signing evidence:
- Runtime/log/UI evidence:
- Cause:
- Fix:
- Relaunch/runtime verification:
- Permissions or signing impact:
- Stop condition or residual risk:
```
