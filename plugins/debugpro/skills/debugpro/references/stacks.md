# Stack-Specific Debugging Cues

Use with `technique-index.md` when the route is chosen but the stack shapes the
first evidence loop.

| Stack | First evidence | Common split |
| --- | --- | --- |
| Web frontend | Route, console, network, component state, screenshot. | Rendering vs data vs hydration vs stale asset. |
| API/backend | Request, handler, logs, DB/API state, auth context. | Input vs business logic vs dependency vs config. |
| CLI | Exact command, args, cwd, env, exit code, stderr. | Parser vs config vs filesystem vs dependency. |
| Worker/job | Queue event, schedule, payload, logs, retry state. | Trigger vs payload vs idempotency vs resource limit. |
| CI | Workflow, job, runner, command, artifact/log. | Code failure vs workflow failure vs runner drift. |
| MCP/plugin | Config, install path, process, discovery, tool call. | Configured vs launched vs exposed vs callable. |
| macOS app | Source, bundle, process, logs, permissions, visible state. | Build vs signing vs runtime vs stale install. |
| Production service | Impact, timeline, deploy, logs, traces, metrics. | Bad deploy vs data vs dependency vs saturation. |

## Rule

Do not let stack familiarity replace proof. Use the stack cue only to choose the
first signal to inspect.
