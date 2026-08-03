# Confirmed Install Execution

Tool Finder v1 does not execute installs. It produces normalized results and dry-run install plans. Confirmed execution can be added after the workflow below is implemented.

## Required User Decision

Before adding execution, decide whether Tool Finder should:

- `plan-only`: never execute installs, always return commands and file changes.
- `confirmed-local-only`: execute only local filesystem plugin/skill copies after explicit confirmation.
- `confirmed-package-manager`: execute package-manager installs after explicit confirmation and environment checks.

The recommended v1 default is `plan-only`.

## Confirmation Contract

Execution must require a fresh confirmation that names:

- The selected tool name, source, and version or commit.
- The exact command or file copy that will run.
- The destination path or package manager target.
- The files and directories that may change.
- The rollback command or manual rollback path.

Follow the user-level requesting-user-input contract. Prefer the User Questions Tweaker's `user_questions` tool for adoption, installation, and approval decisions; use native `request_user_input` as the fallback, then one concise chat question when neither structured tool is available. Tool discovery and comparison remain read-only and should not prompt unless a user-owned decision is genuinely required. Keep risky installation approval isolated from ordinary preferences.

## Allowed Execution Targets

Start with the smallest useful set:

- Local plugin marketplace copy into `~/.agents/plugins/plugins/<plugin-name>`.
- Local skill copy into the configured user skills directory.
- MCP config draft generation into a user-approved config path.

Defer package-manager execution until rollback and supply-chain checks are stronger:

- `npm install -g`.
- `pipx install`.
- `pip install`.
- Homebrew, curl, shell pipes, or remote install scripts.

## Safety Gates

Before execution, Tool Finder must collect and show:

- Source URL and source trust.
- License when available.
- Last update or release date when available.
- Known vulnerability metadata when available.
- Whether install scripts, hooks, or post-install commands may run.
- Whether authentication or secrets are required.

Reject execution by default when:

- The command uses `curl | sh`, `wget | sh`, or an equivalent remote shell pipe.
- The source is archived, deleted, or missing.
- The result has no source URL or no version/commit identity.
- The install would overwrite an existing plugin, skill, MCP config, or global package without a backup plan.
- The tool requires secrets that are not already configured through a proper secret store.

## Rollback

Every execution plan must include:

- A pre-change backup path for file copies.
- An uninstall command for package-manager installs.
- A list of created files.
- A list of modified files.
- A restore step that can be run without network access for local file changes.

Rollback metadata should be written as JSON next to the execution log.

## Execution Log

When execution is eventually enabled, write one JSON log per install:

```json
{
  "tool": "example-tool",
  "source": "npm",
  "selectedResultId": "npm:example-tool",
  "confirmedAt": "2026-06-08T00:00:00Z",
  "command": "npm install -g example-tool",
  "willModify": [],
  "created": [],
  "modified": [],
  "backupPath": null,
  "rollback": [],
  "status": "planned"
}
```

Do not write tokens, API keys, personal email addresses, or raw secret values to this log.
