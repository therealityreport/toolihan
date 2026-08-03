#!/usr/bin/env python3
"""Create provider plans for npm, Python, and Homebrew."""

from __future__ import annotations

import argparse

from tool_finder_common import dump_json


PROVIDERS = {
    "npm": ["live search through scripts/search_npm.py", "package metadata", "bin entries", "dry-run install command"],
    "python": ["live unified metadata and install plans through scripts/search_python.py", "PyPI project metadata", "pip dry-run report command", "pipx CLI install command"],
    "pypi": ["compatibility alias; use scripts/search_python.py for unified Python provider results", "PyPI project metadata", "known vulnerability metadata"],
    "homebrew": ["live metadata through scripts/search_homebrew.py", "formula metadata", "cask metadata", "dry-run brew install command"],
    "pips": ["compatibility alias; use scripts/search_python.py for unified Python provider results", "pip dry-run report command", "pipx CLI install command"],
}

LIVE_PROVIDERS = {"npm", "python", "pypi", "homebrew", "pips"}
PROVIDER_SCRIPTS = {
    "npm": "scripts/search_npm.py",
    "python": "scripts/search_python.py",
    "pypi": "scripts/search_python.py",
    "homebrew": "scripts/search_homebrew.py",
    "pips": "scripts/search_python.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="CLI, MCP server, or package capability to plan for.")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), action="append")
    args = parser.parse_args()

    providers = args.provider or sorted(PROVIDERS)
    dump_json({
        "mode": "package-registry-provider-plan",
        "query": args.query,
        "status": "live-for-npm-python-homebrew",
        "providers": [
            {
                "name": provider,
                "officialSources": PROVIDERS[provider],
                "v1Behavior": "live normalized provider client with dry-run install plan only" if provider in LIVE_PROVIDERS else "deferred provider plan only",
                "autoInstall": False,
                "script": PROVIDER_SCRIPTS.get(provider),
            }
            for provider in providers
        ],
        "notes": [
            "Use official registry APIs or official docs.",
            "Treat popularity/downloads as adoption evidence, not safety evidence.",
            "Do not auto-install registry packages in v1; confirmed install execution is a separately designed workflow.",
        ],
    })


if __name__ == "__main__":
    main()
