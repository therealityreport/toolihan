# Language Matrix

Use when language or runtime conventions change the evidence to capture.

| Language/runtime | Evidence to capture | Frequent failure shape |
| --- | --- | --- |
| JavaScript/TypeScript | package manager, lockfile, runtime version, bundler, transpiled output. | ESM/CJS mismatch, stale build, type/runtime drift, dependency version. |
| Python | interpreter, venv, `PYTHONPATH`, lockfile, import path, stack trace. | Wrong environment, import shadowing, dependency drift, async boundary. |
| Swift/macOS | Xcode/Swift version, scheme, bundle, signing, entitlements, unified logs. | Bundle drift, permission, signing, main-thread/UI lifecycle. |
| Go | module graph, build tags, binary path, env, race output. | Stale binary, cross-compile flags, data race, context cancellation. |
| Rust | toolchain, feature flags, target, panic/backtrace, cargo lock. | Feature mismatch, lifetime workaround, unsafe boundary, release/debug difference. |
| Java/Kotlin | JDK, Gradle/Maven, classpath, profiles, logs. | Classpath drift, profile config, thread/resource leak. |
| Ruby/PHP | interpreter, gem/composer lock, environment, route logs. | Wrong runtime, autoload/cache, config or migration drift. |

## Rule

Capture the runtime actually executing the failing code, not only the source
language in the repository.
