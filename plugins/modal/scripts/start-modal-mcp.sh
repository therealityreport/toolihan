#!/bin/sh
set -eu

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! command -v node >/dev/null 2>&1; then
  printf '%s\n' "modal-readonly MCP: Node.js is required." >&2
  exit 127
fi

exec node "$script_dir/modal-readonly-mcp.mjs" "$@"
