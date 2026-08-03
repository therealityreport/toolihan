# macOS Debugging

Use when a macOS app, menu bar app, Swift/Objective-C code, signing, entitlement,
bundle, launch service, permission, or visible desktop behavior is involved.

## Evidence To Capture

- Source path, built app bundle, installed app bundle, process command, and version.
- `xcodebuild` or SwiftPM command and exact failure.
- Unified logs, crash logs, sandbox/signing/entitlement output, and permission state.
- Visible app/window/menu state when UI behavior is the symptom.
- Difference between debug build, release build, installed app, and running process.

## First Probes

- Confirm which bundle is running before editing.
- Read logs around launch or the failing action.
- Separate build failure, signing failure, runtime crash, permission failure, and stale installed bundle.
- Use GUI proof when the user reported visible desktop state.

## Stop Conditions

- Accessibility, automation, or system permission is required and unavailable.
- Reinstalling or killing the app would disrupt unrelated user work.
- Signing or notarization changes require credentials or identity decisions.

## Handoff Line

`macOS proof: source=<path>, bundle=<path>, pid=<pid>, logs=<summary>, visible=<state>.`
