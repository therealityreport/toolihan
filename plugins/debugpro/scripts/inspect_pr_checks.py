#!/usr/bin/env python3
"""Inspect GitHub pull request checks through the local gh CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from debugpro_context_commands import run_command


def run_gh(args: Sequence[str], cwd: Path, timeout: int = 20) -> dict[str, object]:
    result = run_command(("gh", *args), cwd, timeout)
    if not result.get("available"):
        result["error"] = "gh CLI is not installed"
        return result
    stdout = result.get("stdout")
    if isinstance(stdout, str):
        try:
            result["stdout"] = json.loads(stdout) if stdout else None
        except json.JSONDecodeError:
            pass
    return result


def inspect_pr(cwd: Path, pr: str | None, repo: str | None) -> dict[str, object]:
    base_args: list[str] = []
    if repo:
        base_args.extend(["--repo", repo])
    selector = [pr] if pr else []
    view_fields = "number,url,headRefName,baseRefName,state,statusCheckRollup"
    checks_fields = "name,link,state,workflow,bucket,description,startedAt,completedAt"
    return {
        "pr": run_gh(["pr", "view", *selector, *base_args, "--json", view_fields], cwd),
        "checks": run_gh(["pr", "checks", *selector, *base_args, "--json", checks_fields], cwd),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect GitHub PR checks with gh.")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Repository checkout.")
    parser.add_argument("--pr", help="Pull request number, URL, or branch. Defaults to current branch.")
    parser.add_argument("--repo", help="OWNER/REPO for gh --repo.")
    args = parser.parse_args(argv)

    result = inspect_pr(args.cwd, args.pr, args.repo)
    print(json.dumps(result, indent=2, sort_keys=True))
    failures = [
        item
        for item in result.values()
        if isinstance(item, dict) and item.get("returncode") not in (None, 0)
    ]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
