#!/usr/bin/env python3
"""Export or normalize a runtime connector catalog for Tool Finder."""

from __future__ import annotations

import argparse
from typing import Any

from tool_finder_common import dump_json, load_payload


KNOWN_CONNECTORS = [
    {
        "id": "mcp__codex_apps__github",
        "name": "GitHub connector",
        "namespace": "mcp__codex_apps__github",
        "plugin": "github",
        "connector": "GitHub",
        "description": "GitHub plugin connector tools available in the current Codex session.",
    },
    {
        "id": "mcp__codex_apps__hugging_face",
        "name": "Hugging Face connector",
        "namespace": "mcp__codex_apps__hugging_face",
        "plugin": "hugging-face",
        "connector": "Hugging Face",
        "description": "Hugging Face plugin connector tools available in the current Codex session.",
    },
]


def template() -> dict[str, Any]:
    return {
        "mode": "runtime-connector-catalog-template",
        "tools": KNOWN_CONNECTORS,
        "instructions": [
            "Populate tools with the callable tool metadata exposed in the current assistant session.",
            "Keep plugin values stable, such as github or hugging-face.",
            "Pass this JSON to scripts/search_runtime_tools.py or scripts/search_all_providers.py --runtime-catalog.",
        ],
        "limitations": [
            "A shell script cannot directly inspect live MCP tools from Codex; the assistant must provide the current tool metadata.",
        ],
    }


def normalize_tool(raw: dict[str, Any]) -> dict[str, Any]:
    name = raw.get("name") or raw.get("tool") or raw.get("namespace") or raw.get("id") or "runtime-tool"
    namespace = raw.get("namespace") or raw.get("server") or raw.get("id")
    plugin = raw.get("plugin") or raw.get("pluginName") or raw.get("provider")
    connector = raw.get("connector") or raw.get("connectorName") or raw.get("app")
    description = raw.get("description") or raw.get("summary") or "Callable runtime connector tool."
    return {
        "id": raw.get("id") or namespace or name,
        "name": name,
        "namespace": namespace,
        "plugin": plugin,
        "connector": connector,
        "description": description,
        "source": raw.get("source") or "runtime",
    }


def normalize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        tools = payload
    elif isinstance(payload, dict):
        tools = payload.get("tools") or payload.get("results") or payload.get("connectors") or []
    else:
        tools = []
    normalized = [normalize_tool(tool) for tool in tools if isinstance(tool, dict)]
    return {
        "mode": "runtime-connector-catalog",
        "tools": normalized,
        "counts": {
            "tools": len(normalized),
        },
        "notes": [
            "This catalog is a handoff artifact for Tool Finder provider discovery.",
            "It records plugin connector availability; it does not call connector APIs by itself.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Raw runtime tool metadata JSON. Omit with --template.")
    parser.add_argument("--template", action="store_true", help="Emit a fillable runtime connector catalog template.")
    args = parser.parse_args()

    if args.template or not args.input:
        dump_json(template())
        return
    dump_json(normalize_payload(load_payload(args.input)))


if __name__ == "__main__":
    main()
