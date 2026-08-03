# MCP Runtime Ownership

Use when an MCP server, connector, plugin tool, app tool, or runtime bridge is
configured but not exposed, callable, authenticated, or owned by the expected layer.

## Evidence To Capture

- User-level, project-level, and runtime MCP config files.
- Installed package/plugin path, generated cache path, and active process command.
- Tool discovery output, exposed server names, and failed call error.
- Auth status, environment variables, wrapper scripts, and launch profile.
- Logs from startup, handshake, stderr, and health checks.

## Transport & Logging

- stdio transport: all messages a server logs to stderr are captured by the host application automatically — this is where a stdio server's structured logs land, so read the client log files for stderr output. Local servers must NOT log to stdout — it interferes with protocol operation; route all server logs to stderr.
- Streamable HTTP transport: stderr is NOT captured by the client. Use `notifications/message` log notifications, your own server-side log aggregation, or HTTP tooling (curl, browser DevTools Network panel) to inspect requests, `Mcp-Session-Id` headers, and SSE streams.
- Log notifications carry one of eight RFC 5424 severity levels (`debug` through `emergency`); a client can set the minimum level at runtime via `logging/setLevel`.
- Claude Desktop log files: `~/Library/Logs/Claude` (macOS), `%APPDATA%\Claude\logs` (Windows). They capture server connection events, configuration issues, runtime errors, and message exchanges.
  - macOS: `tail -n 20 -F ~/Library/Logs/Claude/mcp*.log`
  - Windows: `type "$env:AppData\Claude\logs\mcp*.log"`
- Events worth logging (and worth looking for when triaging): initialization steps, resource access, tool execution, error conditions, performance metrics.
- Capability negotiation (-32602): `-32602` is the standard JSON-RPC "Invalid params" code and is returned in many contexts. One common cause is a server sending sampling or elicitation requests to a client that has not declared that capability. Inspect the `initialize` exchange to verify both sides declared what you expect.

## Config, CWD & Env Rules

- A stdio server's launch working directory is undefined (often `/` on macOS) because the client may start from anywhere — use ABSOLUTE paths in both the config args and any referenced `.env` file. Relative paths like `./data` are a primary launch-failure cause.
- Over stdio the server inherits only a limited, platform-dependent subset of env vars, so required variables must be declared explicitly under an `env` key in the server config rather than assumed from the ambient shell.
- When validating the Launched stage, confirm: `command` is an absolute path, all path args/`.env` entries are absolute, the config block is valid JSON with required fields, and every needed env var is supplied via `env`.

## Client-Side Inspection (Chrome DevTools)

To inspect client-side errors and raw message payloads inside Claude Desktop, enable DevTools by creating a `developer_settings.json` with `allowDevTools` true:

```bash
echo '{"allowDevTools": true}' > ~/Library/Application\ Support/Claude/developer_settings.json
```

Then open DevTools with `Command-Option-I` (macOS) / `Ctrl+Alt+I` (Windows). Two DevTools windows appear (main content + app title bar). Use the Console panel for client-side errors and the Network panel for message payloads and connection timing.

## Ownership Split

- Configured: present in config file.
- Installed: package or plugin files exist.
- Launched: process starts with the expected command and environment.
- Negotiated: the `initialize` exchange completed with a mutually supported protocol version and both sides declared the capabilities the workflow needs (e.g. sampling, elicitation).
- Exposed: runtime lists the server and tools.
- Callable: a tool call succeeds with expected auth and permissions.

## Stop Conditions

- Credentials are missing or expired and cannot be refreshed in-session.
- Multiple configs claim the same server and ownership cannot be resolved safely.
- Repair would disable unrelated user-global capabilities.

## Handoff Line

`MCP ownership: configured=<yes/no>, installed=<yes/no>, launched=<yes/no>, negotiated=<yes/no>, exposed=<yes/no>, callable=<yes/no>.`
