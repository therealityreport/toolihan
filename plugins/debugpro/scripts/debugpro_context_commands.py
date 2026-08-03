"""Command and environment helpers for DebugPro context collection."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from debugpro_redaction import redact_output, redact_text


SENSITIVE_ENV_PARTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "COOKIE", "SESSION")


def run_command(command: Sequence[str], cwd: Path, timeout: int = 8) -> dict[str, object]:
    executable = shutil.which(command[0])
    safe_command = [redact_text(part) for part in command]
    if executable is None:
        return {"command": safe_command, "available": False}
    try:
        completed = subprocess.run(
            [executable, *command[1:]],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": safe_command,
            "available": True,
            "timeout": timeout,
            "stdout": redact_output(exc.stdout),
            "stderr": redact_output(exc.stderr),
        }
    return {
        "command": safe_command,
        "available": True,
        "returncode": completed.returncode,
        "stdout": redact_output(completed.stdout.strip()),
        "stderr": redact_output(completed.stderr.strip()),
    }


def safe_environment() -> dict[str, str]:
    keys = (
        "CI",
        "CODESPACES",
        "GITHUB_ACTIONS",
        "LANG",
        "NODE_ENV",
        "PATH",
        "PWD",
        "SHELL",
        "TERM",
        "TZ",
        "VIRTUAL_ENV",
    )
    result: dict[str, str] = {}
    for key in keys:
        if key in os.environ:
            result[key] = "<redacted>" if any(part in key.upper() for part in SENSITIVE_ENV_PARTS) else os.environ[key]
    return result
