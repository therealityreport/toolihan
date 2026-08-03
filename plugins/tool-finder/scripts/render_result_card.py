#!/usr/bin/env python3
"""Render normalized Tool Finder results as readable cards."""

from __future__ import annotations

import argparse

from tool_finder_common import add_input_arg, load_payload, result_list


def render(item: dict) -> str:
    install = item.get("install", {})
    location = item.get("location", {})
    safety = item.get("safety", {})
    provider = item.get("providerStatus") or {}
    provider_name = provider.get("provider") or item.get("source", "unknown")
    provider_variant = f":{provider['variant']}" if provider.get("variant") else ""
    provider_state = provider.get("state") or "unknown"
    lines = [
        f"## [#{item.get('rank', '?')} {item.get('bucket', 'reference')} {item.get('score', 0)}] {item.get('name', 'Unnamed tool')}",
        "",
        f"Type: {item.get('assetType', 'unknown')}",
        f"Source: {item.get('source', 'unknown')}",
        f"Provider source: {item.get('providerSource', 'unknown')}",
        f"Provider: {provider_name}{provider_variant} ({provider_state})",
        f"Status: {install.get('status', 'unknown')}",
        f"Best action: {item.get('recommendedAction', 'reference-only')}",
        "",
        "Why it matched:",
    ]
    reasons = item.get("reasons") or ["No match reason recorded."]
    lines.extend(f"- {reason}" for reason in reasons[:3])
    if provider.get("skipped") or provider.get("reason"):
        lines.extend(["", "Provider status:"])
        lines.append(f"- {provider.get('reason') or provider_state}")
        for remediation in (provider.get("remediation") or [])[:2]:
            lines.append(f"- {remediation}")
    lines.extend(["", "Risks:"])
    risks = safety.get("notes") or item.get("penalties") or ["No specific risk noted."]
    lines.extend(f"- {risk}" for risk in risks[:3])
    lines.extend(["", "Use or install:"])
    use_path = install.get("command") or install.get("installUrl") or location.get("localPath") or location.get("url") or "No direct use path recorded."
    lines.append(f"- {use_path}")

    if item.get("usageExamples"):
        lines.extend(["", "Similar usage:"])
        for example in item["usageExamples"][:3]:
            lines.append(f"- {example.get('repo', 'unknown')}:{example.get('path', '')} - {example.get('whyRelevant', '')}")
    if item.get("alternatives"):
        lines.extend(["", "Alternatives:"])
        for alternative in item["alternatives"][:3]:
            lines.append(f"- {alternative.get('name', 'unknown')} - {alternative.get('whyConsider', '')}")
    if item.get("rejectionReason"):
        lines.extend(["", f"Rejected because: {item['rejectionReason']}"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_input_arg(parser)
    args = parser.parse_args()

    cards = [render(item) for item in result_list(load_payload(args.input))]
    print("\n\n".join(cards))


if __name__ == "__main__":
    main()
