#!/usr/bin/env python3
"""Explain and diagnose GitHub code-search auth for Tool Finder."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from typing import Any

from tool_finder_common import dump_json


def run(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=20)
    except FileNotFoundError:
        return 127, "Command not found."
    except subprocess.TimeoutExpired:
        return 124, "Command timed out."
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode, output[:4000]


def gh_token_available(gh_path: str | None) -> bool:
    if not gh_path:
        return False
    status_code, output = run([gh_path, "auth", "token"])
    return status_code == 0 and bool(output.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-env", default="GITHUB_TOKEN", help="Environment variable Tool Finder should read for GitHub code search.")
    parser.add_argument("--use-gh-token", action="store_true", help="Use GitHub CLI auth as the token source for Tool Finder child processes without printing the token.")
    args = parser.parse_args()

    token_present = bool(os.environ.get(args.token_env))
    gh_path = shutil.which("gh")
    gh_status: dict[str, Any] = {
        "available": bool(gh_path),
        "path": gh_path,
        "authenticated": False,
        "rawStatus": None,
    }
    if gh_path:
        status_code, status_output = run([gh_path, "auth", "status", "-h", "github.com"])
        gh_status["authenticated"] = status_code == 0
        gh_status["rawStatus"] = status_output
    gh_status["tokenAvailable"] = gh_token_available(gh_path) if args.use_gh_token else None

    remediations: list[str] = []
    if token_present:
        state = "ready"
        reason = f"{args.token_env} is set. Tool Finder can attempt GitHub code search."
        effective_ready = True
        token_source = "environment"
    elif args.use_gh_token and gh_status["tokenAvailable"]:
        state = "ready-from-gh"
        reason = "GitHub CLI can provide a token for Tool Finder child processes."
        effective_ready = True
        token_source = "github-cli"
        remediations.extend([
            "Run Tool Finder with --use-gh-token to use GitHub CLI auth without exporting a token.",
            f"To persist shell auth instead, run: export {args.token_env}=$(gh auth token)",
        ])
    elif gh_status["authenticated"]:
        state = "needs-env-export"
        reason = f"{args.token_env} is not set, but GitHub CLI appears authenticated."
        effective_ready = False
        token_source = "none"
        remediations.extend([
            "Run Tool Finder with --use-gh-token to use GitHub CLI auth for this run.",
            f"Run: export {args.token_env}=$(gh auth token)",
            "Then rerun Tool Finder without --no-github-code.",
        ])
    else:
        state = "needs-auth"
        reason = f"{args.token_env} is not set and GitHub CLI auth was not confirmed."
        effective_ready = False
        token_source = "none"
        remediations.extend([
            "Authenticate GitHub CLI with: gh auth login",
            f"Or set {args.token_env} to a GitHub token that can use code search.",
            "Then rerun Tool Finder without --no-github-code.",
        ])

    dump_json({
        "mode": "github-code-auth-helper",
        "provider": "github",
        "variant": "code",
        "state": state,
        "ready": effective_ready,
        "reason": reason,
        "tokenEnv": {
            "name": args.token_env,
            "present": token_present,
            "valuePrinted": False,
            "effectiveSource": token_source,
        },
        "githubCli": gh_status,
        "useGhToken": args.use_gh_token,
        "remediation": remediations,
        "providerStatus": {
            "provider": "github",
            "variant": "code",
            "state": "available" if effective_ready else "skipped",
            "searched": False,
            "skipped": not effective_ready,
            "requiresAuth": True,
            "reason": reason,
            "remediation": remediations,
            "resultCount": 0,
        },
        "notes": [
            "This helper does not print or store tokens.",
            "Tool Finder uses the token only for GitHub REST code search.",
            "The --use-gh-token option can make a child Tool Finder run ready without exporting a token in the parent shell.",
        ],
    })


if __name__ == "__main__":
    main()
