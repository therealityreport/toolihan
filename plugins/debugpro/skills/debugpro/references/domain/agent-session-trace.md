# Agent Session Trace

Use when the failure involves agent behavior, session state, delegated work,
tool-call ordering, handoffs, or confusing multi-agent coordination.

## Evidence To Capture

- User request, active instructions, ownership scope, and allowed files.
- Agent messages, tool calls, outputs, errors, and timestamps.
- Current working directory, branch/worktree state, and edited files.
- Delegation packet, route decision, or handoff report if present.
- Differences between intended plan and executed actions.

## First Probes

- Reconstruct the timeline from durable logs or visible transcript.
- Separate instruction conflict, stale context, tool failure, concurrency conflict, and bad assumption.
- Identify the first unsupported claim or action.
- Preserve exact command/error pairs for repeated failures.

## Stop Conditions

- Session logs are missing and behavior cannot be reproduced.
- Ownership is ambiguous because multiple workers touched the same file.
- The next action would overwrite another worker's changes.

## Handoff Line

`Agent trace: request=<summary>, first divergence=<event>, evidence=<tool/log/message>, owner=<current/unknown>.`
