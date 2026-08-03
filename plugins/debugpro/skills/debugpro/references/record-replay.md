# Record And Replay

Use when timing, ordering, user actions, network payloads, event streams, or
large inputs make a failure hard to reproduce.

## What To Record

- Exact command, route, user action sequence, seed, input, payload, and timestamp.
- Browser console/network logs, HAR, screenshots, or trace where available.
- Queue events, webhook payloads, request IDs, and retry metadata.
- Data snapshot or sanitized fixture needed to replay safely.

## Replay Rules

- Replay in the safest environment that preserves the failure.
- Keep one variable changed at a time.
- Record whether the failure is deterministic, intermittent, or not reproducible.
- Reduce the replay case with `debugpro-delta` when it is too large.

## Stop Conditions

- Replay would mutate production, send external messages, charge money, or leak private data.
- Required payloads or credentials are unavailable.
- The replay no longer matches the original symptom.
