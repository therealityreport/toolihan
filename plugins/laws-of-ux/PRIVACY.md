# Privacy

`laws-of-ux` is a local Claude Code / Codex plugin. It reads files in the project you point it
at, in order to audit the UI against the Laws of UX. It does not send your source code anywhere
on its own.

- **Static audit:** runs entirely locally over your filesystem using the agent's Read/Grep/Glob
  tools. No network calls.
- **`--url` live audit (optional):** drives a browser via the separately installed
  `chrome-devtools` MCP against the URL you provide. That navigates to and measures the page you
  name — use it only against apps you control or are authorized to test.
- **No telemetry.** The plugin has no analytics and collects nothing.

Any report or HTML scorecard is written only where you ask (inline, `--out`, or the audit
output folder). Review generated files before sharing them, since they can quote snippets of
your source.
