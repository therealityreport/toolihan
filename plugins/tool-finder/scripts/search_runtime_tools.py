#!/usr/bin/env python3
"""Normalize a supplied Codex runtime tool catalog into Tool Finder results."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json, load_payload, normalize_result, provider_status, score_result


def plugin_slug(tool: dict) -> str:
    raw = tool.get("plugin") or tool.get("connector") or tool.get("provider") or ""
    return str(raw).strip().lower().replace("_", "-").replace(" ", "-")


def connector_source(tool: dict) -> str:
    slug = plugin_slug(tool)
    if slug in {"github", "git-hub"}:
        return "github-connector"
    if slug in {"hugging-face", "huggingface", "hf"}:
        return "hugging-face-connector"
    return "runtime"


def connector_asset_type(tool: dict) -> str:
    if tool.get("plugin") or tool.get("connector"):
        return "connector"
    return "tool-schema"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", nargs="?", default="-", help="Runtime catalog JSON file, or stdin.")
    args = parser.parse_args()

    payload = load_payload(args.catalog)
    tools = payload if isinstance(payload, list) else payload.get("tools", [])
    results = []
    status_counts: dict[tuple[str, str], int] = {}
    for tool in tools:
        name = tool.get("name") or tool.get("namespace") or tool.get("id") or "runtime-tool"
        description = tool.get("description") or "Callable runtime tool."
        source = connector_source(tool)
        provider = plugin_slug(tool) or "runtime"
        variant = "connector" if source != "runtime" else "catalog"
        status_counts[(provider, variant)] = status_counts.get((provider, variant), 0) + 1
        results.append(
            score_result(
                normalize_result(
                    name=name,
                    asset_type=connector_asset_type(tool),
                    source=source,
                    status="already-available",
                    action="use-now",
                    reasons=[description],
                    source_trust="first-party" if tool.get("plugin") or tool.get("connector") else "unknown",
                    ownership="callable-now",
                    external_ids={
                        "sourceType": "runtime-connector" if source != "runtime" else "runtime-tool",
                        "runtimeToolId": tool.get("id") or name,
                        "plugin": tool.get("plugin"),
                        "connector": tool.get("connector"),
                        "namespace": tool.get("namespace"),
                    },
                    provider_source="connector-plugin" if source != "runtime" else "runtime-catalog",
                    provider_status=provider_status(
                        provider,
                        variant=variant,
                        state="available",
                        searched=True,
                        reason="Callable plugin connector was present in the supplied runtime catalog." if source != "runtime" else "Callable runtime tool was present in the supplied runtime catalog.",
                        result_count=None,
                    ),
                )
            )
        )
    for result in results:
        status = result.get("providerStatus") or {}
        key = (status.get("provider") or "runtime", status.get("variant") or "catalog")
        status["resultCount"] = status_counts.get(key, 0)
        result["providerStatus"] = status
    dump_json({
        "mode": "runtime-connector-catalog-search",
        "providerStatus": [
            provider_status(
                provider,
                variant=variant,
                state="available",
                searched=True,
                reason="Callable plugin connector was present in the supplied runtime catalog." if variant == "connector" else "Callable runtime tool was present in the supplied runtime catalog.",
                result_count=count,
            )
            for (provider, variant), count in sorted(status_counts.items())
        ],
        "results": results,
    })


if __name__ == "__main__":
    main()
