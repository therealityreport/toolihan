#!/usr/bin/env python3
"""Collect read-only Git context for a bug investigation."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run(repo: Path, args: list[str]) -> dict[str, object]:
    try:
        proc = subprocess.run(
            args,
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc), "stdout": "", "stderr": ""}

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def default_base(repo: Path) -> str:
    head = run(repo, ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"])
    if head["ok"] and head["stdout"]:
        return str(head["stdout"]).removeprefix("origin/")
    for candidate in ("main", "master", "develop"):
        exists = run(repo, ["git", "rev-parse", "--verify", "--quiet", candidate])
        if exists["ok"]:
            return candidate
    return "HEAD~1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect read-only bug investigation context.")
    parser.add_argument("--repo", default=".", help="Repository path.")
    parser.add_argument("--base", help="Diff base. Defaults to origin HEAD, main, master, develop, or HEAD~1.")
    ns = parser.parse_args()

    repo = Path(ns.repo).expanduser().resolve()
    if not repo.exists():
        print(json.dumps({"ok": False, "error": f"repo does not exist: {repo}"}, indent=2))
        return 2

    root = run(repo, ["git", "rev-parse", "--show-toplevel"])
    if not root["ok"]:
        print(json.dumps({"ok": True, "repo": str(repo), "is_git": False}, indent=2))
        return 0

    repo = Path(str(root["stdout"]))
    base = ns.base or default_base(repo)
    payload = {
        "ok": True,
        "is_git": True,
        "repo": str(repo),
        "base": base,
        "status": run(repo, ["git", "status", "--short"]),
        "changed_files": run(repo, ["git", "diff", "--name-status", f"{base}...HEAD"]),
        "diff_stat": run(repo, ["git", "diff", "--stat", f"{base}...HEAD"]),
        "recent_commits": run(repo, ["git", "log", "--oneline", "-12"]),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
