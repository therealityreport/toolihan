#!/usr/bin/env python3
"""Run the read-only universal-role doctor for setup-command compatibility."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


NO_PROJECT_WORKERS = "Codex Improve no longer creates project-local worker files."
MINIMUM_DOCTOR_PYTHON = (3, 11)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Deprecated compatibility argument. It is reported but never written.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex home that owns the universal role catalog.",
    )
    parser.add_argument(
        "--routing-root",
        type=Path,
        help="Override the global subagent-routing skill root for validation or recovery.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        action="append",
        default=[],
        help="Deprecated compatibility argument. It is ignored because role selection is global.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Deprecated compatibility argument. Setup performs no write and never prompts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Deprecated compatibility argument. Setup is always read-only.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a stable compatibility report.")
    return parser.parse_args()


def compatibility_options(args: argparse.Namespace) -> list[str]:
    options = ["--project"]
    if args.yes:
        options.append("--yes")
    if args.dry_run:
        options.append("--dry-run")
    if args.catalog:
        options.append("--catalog")
    return options


def supported_python(candidate: str) -> bool:
    try:
        probe = subprocess.run(
            [
                candidate,
                "-c",
                "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return probe.returncode == 0


def doctor_python() -> str | None:
    candidates = [
        sys.executable,
        *(shutil.which(name) for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3")),
        "/opt/homebrew/bin/python3",
        "/usr/local/bin/python3",
    ]
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if supported_python(candidate):
            return candidate
    return None


def report(
    *,
    status: str,
    project: Path,
    codex_home: Path,
    doctor: Path,
    doctor_python_path: str | None,
    options: list[str],
    doctor_report: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "compatibility": {
            "message": NO_PROJECT_WORKERS,
            "project": str(project),
            "createdProjectWorkers": False,
            "ignoredLegacyOptions": options,
        },
        "codexHome": str(codex_home),
        "doctor": str(doctor),
        "doctorPython": doctor_python_path,
    }
    if doctor_report is not None:
        payload["doctorReport"] = doctor_report
    if error is not None:
        payload["error"] = error
    return payload


def emit(payload: dict[str, Any], as_json: bool, doctor_stdout: str = "", doctor_stderr: str = "") -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print(NO_PROJECT_WORKERS)
    print(f"Checking global universal roles with: {payload['doctor']}")
    if payload["doctorPython"] is not None:
        print(f"Using doctor interpreter: {payload['doctorPython']}")
    if payload["compatibility"]["ignoredLegacyOptions"]:
        options = ", ".join(payload["compatibility"]["ignoredLegacyOptions"])
        print(f"Compatibility-only arguments ignored: {options}")
    if doctor_stdout.strip():
        print(doctor_stdout.rstrip())
    if doctor_stderr.strip():
        print(doctor_stderr.rstrip(), file=sys.stderr)
    if payload["status"] != "ok":
        print(f"Setup compatibility check blocked: {payload['error']}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    codex_home = args.codex_home.expanduser().resolve()
    routing_root = (args.routing_root or codex_home / "skills" / "subagent-routing").expanduser().resolve()
    doctor = routing_root / "scripts" / "sync-universal-roles.py"
    options = compatibility_options(args)
    doctor_python_path = doctor_python()

    if not doctor.is_file():
        payload = report(
            status="blocked",
            project=project,
            codex_home=codex_home,
            doctor=doctor,
            doctor_python_path=doctor_python_path,
            options=options,
            error="The global universal-role doctor is unavailable.",
        )
        emit(payload, args.json)
        return 2

    if doctor_python_path is None:
        payload = report(
            status="blocked",
            project=project,
            codex_home=codex_home,
            doctor=doctor,
            doctor_python_path=None,
            options=options,
            error=(
                "The global universal-role doctor requires Python "
                f"{MINIMUM_DOCTOR_PYTHON[0]}.{MINIMUM_DOCTOR_PYTHON[1]} or newer."
            ),
        )
        emit(payload, args.json)
        return 2

    command = [
        doctor_python_path,
        str(doctor),
        "--check",
        "--json",
        "--codex-home",
        str(codex_home),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    doctor_report: dict[str, Any] | None = None
    error: str | None = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            error = "The global doctor did not emit valid JSON."
        else:
            if isinstance(parsed, dict):
                doctor_report = parsed
            else:
                error = "The global doctor emitted an invalid report shape."
    else:
        error = "The global doctor emitted no JSON report."

    if completed.returncode != 0:
        error = error or f"The global doctor exited with status {completed.returncode}."
    elif doctor_report is not None and doctor_report.get("status") != "ok":
        error = f"The global doctor reported status {doctor_report.get('status')!r}."

    payload = report(
        status="ok" if error is None else "blocked",
        project=project,
        codex_home=codex_home,
        doctor=doctor,
        doctor_python_path=doctor_python_path,
        options=options,
        doctor_report=doctor_report,
        error=error,
    )
    emit(payload, args.json, completed.stdout, completed.stderr)
    return 0 if error is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
