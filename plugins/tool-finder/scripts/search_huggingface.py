#!/usr/bin/env python3
"""Search public Hugging Face Hub models, datasets, and Spaces."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from tool_finder_common import dump_json, normalize_result, provider_status, score_result


API_BASE = "https://huggingface.co/api"
SITE_BASE = "https://huggingface.co"
USER_AGENT = "tool-finder/0.1 (+https://huggingface.co/docs/hub/en/api)"


def request_json(path: str, *, token_env: str, timeout: int = 30) -> tuple[Any, dict[str, str | None]]:
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get(token_env)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API_BASE}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), {
                "rateLimitRemaining": response.headers.get("X-RateLimit-Remaining"),
                "cacheUntil": response.headers.get("Cache-Control"),
                "etag": response.headers.get("ETag"),
            }
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:4000]
        raise SystemExit(json.dumps({
            "error": "Hugging Face request failed",
            "status": error.code,
            "path": path,
            "requiresAuth": error.code in {401, 403},
            "body": body,
        }, indent=2))
    except urllib.error.URLError as error:
        raise SystemExit(json.dumps({
            "error": "Hugging Face request failed",
            "path": path,
            "reason": str(error.reason),
        }, indent=2))


def endpoint(kind: str, query: str, limit: int) -> str:
    params = urllib.parse.urlencode({
        "search": query,
        "limit": max(1, min(limit, 100)),
        "full": "true",
    })
    if kind == "models":
        return f"/models?{params}"
    if kind == "datasets":
        return f"/datasets?{params}"
    if kind == "spaces":
        return f"/spaces?{params}"
    raise ValueError(f"Unsupported Hugging Face kind: {kind}")


def repo_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("modelId") or item.get("repoId") or item.get("name") or "unknown")


def url_for(kind: str, repo: str) -> str:
    if kind == "models":
        return f"{SITE_BASE}/{repo}"
    if kind == "datasets":
        return f"{SITE_BASE}/datasets/{repo}"
    return f"{SITE_BASE}/spaces/{repo}"


def tags(item: dict[str, Any]) -> list[str]:
    value = item.get("tags") or []
    return [str(tag) for tag in value if tag]


def tag_value(tag_values: list[str], prefix: str) -> str | None:
    for tag in tag_values:
        if tag.startswith(prefix):
            return tag[len(prefix):]
    return None


def normalize_hf_item(item: dict[str, Any], *, kind: str, evidence: dict[str, Any], query: str) -> dict[str, Any]:
    repo = repo_id(item)
    tag_values = tags(item)
    downloads = item.get("downloads")
    likes = item.get("likes")
    pipeline = item.get("pipeline_tag") or item.get("pipelineTag")
    sdk = item.get("sdk") or item.get("spaceSdk")
    license_name = item.get("license") or tag_value(tag_values, "license:")
    library_name = item.get("library_name") or item.get("libraryName") or tag_value(tag_values, "library:")
    gated = item.get("gated")
    private = item.get("private")
    asset_type = {"models": "model", "datasets": "dataset", "spaces": "app"}[kind]
    capabilities = [
        value
        for value in [
            f"pipeline: {pipeline}" if pipeline else None,
            f"sdk: {sdk}" if sdk else None,
            f"library: {library_name}" if library_name else None,
            f"license: {license_name}" if license_name else None,
            f"tags: {', '.join(tag_values[:8])}" if tag_values else None,
        ]
        if value
    ]
    risk_notes = ["Review license, model card, dataset card, or Space runtime before adopting."]
    if gated:
        risk_notes.append("Resource is gated and may require accepted access terms.")
    if private:
        risk_notes.append("Resource is private and requires authenticated access.")
    result = normalize_result(
        name=repo,
        asset_type=asset_type,
        source="hugging-face",
        path=repo,
        url=url_for(kind, repo),
        repo=repo,
        status="manual",
        action="reference-only",
        reasons=[
            f"Hugging Face {kind[:-1]} matched the query.",
            f"Pipeline: {pipeline}." if pipeline else "",
            f"SDK: {sdk}." if sdk else "",
            f"Library: {library_name}." if library_name else "",
            f"License: {license_name}." if license_name else "",
            f"Downloads: {downloads}." if downloads is not None else "",
            f"Likes: {likes}." if likes is not None else "",
        ],
        risks=risk_notes,
        source_trust="public-source",
        ownership="remote-third-party",
        external_ids={
            "sourceType": f"hugging-face-{kind[:-1]}",
            "huggingFaceRepoId": repo,
            "huggingFaceKind": kind,
            "pipeline": pipeline,
            "sdk": sdk,
            "library": library_name,
            "license": license_name,
        },
        safety={
            "status": "warn" if (gated or private) else "unknown",
            "riskLevel": "medium" if gated else "high" if private else "unknown",
            "notes": risk_notes,
        },
        maintenance={
            "lastUpdated": item.get("lastModified") or item.get("last_modified"),
            "installs": downloads if isinstance(downloads, int) else None,
            "signals": [
                signal
                for signal in [
                    f"likes:{likes}" if likes is not None else None,
                    f"downloads:{downloads}" if downloads is not None else None,
                    f"private:{private}" if private is not None else None,
                    f"gated:{gated}" if gated is not None else None,
                    f"tags:{len(tag_values)}" if tag_values else None,
                ]
                if signal
            ],
        },
        api_evidence={
            **evidence,
            "searchType": kind,
            "searchQuery": query,
        },
        provider_source="direct-api",
        provider_status=provider_status(
            "hugging-face",
            variant=kind,
            state="queried",
            searched=True,
            reason="Hugging Face Hub public API lookup completed.",
            result_count=None,
        ),
    )
    result["capabilities"] = capabilities
    return score_result(result)


def search(query: str, *, kind: str, limit: int, token_env: str) -> dict[str, Any]:
    kinds = ["models", "datasets", "spaces"] if kind == "all" else [kind]
    results: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    for current_kind in kinds:
        payload, evidence = request_json(endpoint(current_kind, query, limit), token_env=token_env)
        items = payload if isinstance(payload, list) else payload.get("items", []) if isinstance(payload, dict) else []
        kind_results = [
            normalize_hf_item(item, kind=current_kind, evidence=evidence, query=query)
            for item in items[:limit]
            if isinstance(item, dict)
        ]
        for result in kind_results:
            result["providerStatus"]["resultCount"] = len(kind_results)
        results.extend(kind_results)
        statuses.append(provider_status(
            "hugging-face",
            variant=current_kind,
            state="queried",
            searched=True,
            reason="Hugging Face Hub public API lookup completed.",
            result_count=len(kind_results),
        ))
    return {
        "mode": "hugging-face-live-search",
        "provider": "hugging-face",
        "providerSource": "direct-api",
        "query": query,
        "kind": kind,
        "results": results,
        "providerStatus": statuses,
        "notes": [
            "Uses public Hugging Face Hub API endpoints.",
            "A Hugging Face token is optional for public resources and can be supplied through HF_TOKEN.",
            "Results are references; Tool Finder does not download models, datasets, or Spaces.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Model, dataset, Space, task, or capability terms.")
    parser.add_argument("--kind", choices=["all", "models", "datasets", "spaces"], default="all")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--token-env", default="HF_TOKEN", help="Optional Hugging Face token environment variable.")
    args = parser.parse_args()
    dump_json(search(args.query, kind=args.kind, limit=max(1, min(args.limit, 100)), token_env=args.token_env))


if __name__ == "__main__":
    main()
