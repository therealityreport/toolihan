#!/usr/bin/env python3
"""Create GitHub query plans or execute live GitHub REST search."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from tool_finder_common import classify_path, dump_json, normalize_result, score_result


TEMPLATES = [
    'SKILL.md "{topic}"',
    'AGENTS.md "{topic}"',
    '".codex-plugin/plugin.json" "{topic}"',
    '"mcpServers" "{topic}"',
    '".mcp.json" "{topic}"',
    '"package.json" "bin" "{topic}"',
    '"pyproject.toml" "console_scripts" "{topic}"',
    '"hooks" "{topic}" "agent"',
]

API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "tool-finder/0.1 (+https://docs.github.com/rest/search/search)"


def request_json(url: str, *, token: str | None = None, timeout: int = 20) -> tuple[dict[str, Any], dict[str, str | None]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), headers_to_evidence(response.headers)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:4000]
        raise SystemExit(json.dumps({
            "error": "GitHub request failed",
            "status": error.code,
            "url": url,
            "requiresAuth": error.code in {401, 403},
            "body": body,
        }, indent=2))
    except urllib.error.URLError as error:
        raise SystemExit(json.dumps({
            "error": "GitHub request failed",
            "url": url,
            "reason": str(error.reason),
        }, indent=2))


def headers_to_evidence(headers: Any) -> dict[str, str | None]:
    return {
        "rateLimitRemaining": headers.get("X-RateLimit-Remaining"),
        "cacheUntil": None,
        "rateLimitLimit": headers.get("X-RateLimit-Limit"),
        "rateLimitReset": headers.get("X-RateLimit-Reset"),
    }


def apply_scope(query: str, *, org: str | None = None, repo: str | None = None) -> str:
    scoped = query
    if repo:
        scoped = f"{scoped} repo:{repo}"
    elif org:
        scoped = f"{scoped} org:{org}"
    return scoped


def search_url(kind: str, query: str, limit: int) -> str:
    endpoint = "code" if kind == "code" else "repositories"
    params = urllib.parse.urlencode({
        "q": query,
        "per_page": max(1, min(limit, 100)),
    })
    return f"{API_BASE}/search/{endpoint}?{params}"


def infer_repo_asset_type(name: str, description: str | None = None) -> str:
    haystack = f"{name} {description or ''}".lower()
    if "mcp" in haystack or "model context protocol" in haystack:
        return "mcp"
    if "plugin" in haystack:
        return "plugin"
    if "skill" in haystack:
        return "skill"
    if "agent" in haystack:
        return "agent"
    if "cli" in haystack or "command line" in haystack or "command-line" in haystack:
        return "cli"
    return "unknown"


def normalize_code_hit(hit: dict[str, Any], api_evidence: dict[str, Any]) -> dict[str, Any]:
    repo = hit.get("repository") or {}
    path = hit.get("path") or hit.get("name") or "unknown"
    asset_type = classify_path(path)
    result = normalize_result(
        name=f"{repo.get('full_name', 'unknown')}/{path}",
        asset_type=asset_type,
        source="github",
        path=path,
        url=hit.get("html_url"),
        repo=repo.get("full_name"),
        status="manual",
        action="reference-only",
        reasons=[
            f"GitHub code search matched {path}.",
            "Prefer code/config hits over README-only mentions.",
        ],
        risks=["Remote repository content is reference material until reviewed locally."],
        source_trust="public-source",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "github-code",
            "sha": hit.get("sha"),
        },
        safety={
            "status": "unknown",
            "riskLevel": "unknown",
            "notes": ["Do not execute remote code from search results without manual review."],
        },
        maintenance={
            "lastUpdated": repo.get("updated_at"),
            "isArchived": bool(repo.get("archived")),
            "signals": [
                f"stars:{repo.get('stargazers_count')}" if repo.get("stargazers_count") is not None else "",
                f"visibility:{repo.get('visibility')}" if repo.get("visibility") else "",
            ],
        },
        api_evidence={**api_evidence, "searchType": "code"},
    )
    return score_result(result)


def normalize_repository_hit(hit: dict[str, Any], api_evidence: dict[str, Any]) -> dict[str, Any]:
    name = hit.get("full_name") or hit.get("name") or "unknown-repository"
    description = hit.get("description")
    asset_type = infer_repo_asset_type(name, description)
    result = normalize_result(
        name=name,
        asset_type=asset_type,
        source="github",
        path=None,
        url=hit.get("html_url"),
        repo=name,
        status="manual",
        action="reference-only",
        reasons=[
            description or "GitHub repository search matched the query.",
            f"Stars: {hit.get('stargazers_count')}." if hit.get("stargazers_count") is not None else "",
            "Repository result can be used to find implementation patterns and alternatives.",
        ],
        risks=["Remote repository content is reference material until reviewed locally."],
        source_trust="public-source",
        ownership="remote-third-party",
        external_ids={
            "sourceType": "github-repository",
            "githubId": hit.get("id"),
        },
        safety={
            "status": "unknown",
            "riskLevel": "unknown",
            "notes": ["Inspect license, install scripts, and permissions before adopting."],
        },
        maintenance={
            "lastUpdated": hit.get("updated_at") or hit.get("pushed_at"),
            "isArchived": bool(hit.get("archived")),
            "signals": [
                signal
                for signal in [
                    f"stars:{hit.get('stargazers_count')}" if hit.get("stargazers_count") is not None else None,
                    f"forks:{hit.get('forks_count')}" if hit.get("forks_count") is not None else None,
                    f"language:{hit.get('language')}" if hit.get("language") else None,
                ]
                if signal
            ],
        },
        api_evidence={**api_evidence, "searchType": "repositories"},
    )
    return score_result(result)


def live_search(topic: str, *, kind: str, org: str | None, repo: str | None, limit: int, token_env: str) -> dict[str, Any]:
    query = apply_scope(topic, org=org, repo=repo)
    token = os.environ.get(token_env)
    data, evidence = request_json(search_url(kind, query, limit), token=token)
    hits = data.get("items") or []
    normalizer = normalize_code_hit if kind == "code" else normalize_repository_hit
    return {
        "mode": f"github-live-{kind}-search",
        "topic": topic,
        "query": query,
        "provider": "github",
        "requiresAuth": kind == "code" and not token,
        "total": data.get("total_count"),
        "incompleteResults": data.get("incomplete_results"),
        "results": [normalizer(hit, evidence) for hit in hits],
        "notes": [
            "Uses GitHub REST search.",
            "Code search may require a token and is subject to lower rate limits.",
            "Results are references; Tool Finder does not modify remote repositories.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", help="Tool, job, or capability to search for.")
    parser.add_argument("--org", help="Optional GitHub org scope.")
    parser.add_argument("--repo", help="Optional owner/repo scope.")
    parser.add_argument("--live", action="store_true", help="Execute GitHub REST search instead of producing a query plan.")
    parser.add_argument("--type", choices=["code", "repositories"], default="code", help="Search endpoint to use with --live.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum live results, capped at 100.")
    parser.add_argument("--token-env", default="GITHUB_TOKEN", help="Environment variable containing a GitHub token.")
    args = parser.parse_args()

    if args.live:
        dump_json(live_search(
            args.topic,
            kind=args.type,
            org=args.org,
            repo=args.repo,
            limit=max(1, min(args.limit, 100)),
            token_env=args.token_env,
        ))
        return

    dump_json({
        "mode": "github-query-plan",
        "topic": args.topic,
        "org": args.org,
        "repo": args.repo,
        "queries": [template.format(topic=args.topic) for template in TEMPLATES],
        "notes": [
            "Use the GitHub connector search/fetch tools for execution.",
            "Prefer code/config hits over README-only mentions.",
            "Do not write remote GitHub files in v1.",
        ],
    })


if __name__ == "__main__":
    main()
