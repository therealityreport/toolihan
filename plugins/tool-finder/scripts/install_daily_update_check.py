#!/usr/bin/env python3
"""Install Tool Finder's daily update checker as a user launchd job."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import subprocess
from pathlib import Path
from typing import Any


LABEL = "com.thomashulihan.tool-finder.daily-update-check"
LAUNCHD_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"


DEFAULT_CONFIG = {
    "roots": [
        "~/Projects",
        "~/Documents/Codex",
        "~/.agents/plugins/plugins",
        "~/.codex/plugins",
    ],
    "maxDepth": 4,
    "maxProjects": 250,
    "checks": {
        "git": True,
        "npm": True,
        "python": True,
        "homebrew": True,
        "mcp": True,
    },
}


def expand_path(raw: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(raw))).resolve()


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def write_default_config(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DEFAULT_CONFIG, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def plist_payload(*, hour: int, minute: int, config: Path, report_dir: Path, notify: bool, log_dir: Path) -> dict[str, Any]:
    script = plugin_root() / "scripts" / "check_updates_daily.py"
    args = [
        "/usr/bin/env",
        "python3",
        str(script),
        "--config",
        str(config),
        "--report-dir",
        str(report_dir),
    ]
    if notify:
        args.append("--notify")
    log_dir.mkdir(parents=True, exist_ok=True)
    return {
        "Label": LABEL,
        "ProgramArguments": args,
        "StartCalendarInterval": {
            "Hour": hour,
            "Minute": minute,
        },
        "StandardOutPath": str(log_dir / "daily-update-check.out.log"),
        "StandardErrorPath": str(log_dir / "daily-update-check.err.log"),
        "WorkingDirectory": str(plugin_root()),
        "EnvironmentVariables": {
            "PATH": LAUNCHD_PATH,
        },
        "RunAtLoad": False,
    }


def write_plist(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        plistlib.dump(payload, handle, sort_keys=True)


def run(args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    return completed.returncode, completed.stdout, completed.stderr


def load_launchd(plist_path: Path) -> list[dict[str, Any]]:
    uid = os.getuid()
    domain = f"gui/{uid}"
    events = []
    code, stdout, stderr = run(["launchctl", "bootout", domain, str(plist_path)])
    events.append({"command": "launchctl bootout", "code": code, "stdout": stdout.strip(), "stderr": stderr.strip()})
    code, stdout, stderr = run(["launchctl", "bootstrap", domain, str(plist_path)])
    events.append({"command": "launchctl bootstrap", "code": code, "stdout": stdout.strip(), "stderr": stderr.strip()})
    code, stdout, stderr = run(["launchctl", "enable", f"{domain}/{LABEL}"])
    events.append({"command": "launchctl enable", "code": code, "stdout": stdout.strip(), "stderr": stderr.strip()})
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hour", type=int, default=9, help="Local hour for the daily check.")
    parser.add_argument("--minute", type=int, default=0, help="Local minute for the daily check.")
    parser.add_argument("--config", default="~/.agents/tool-finder/update-watch-config.json")
    parser.add_argument("--report-dir", default="~/.agents/tool-finder/reports")
    parser.add_argument("--log-dir", default="~/.agents/tool-finder/logs")
    parser.add_argument("--plist", default=f"~/Library/LaunchAgents/{LABEL}.plist")
    parser.add_argument("--no-notify", action="store_true", help="Do not show macOS notifications.")
    parser.add_argument("--load", action="store_true", help="Load or reload the launchd job now.")
    args = parser.parse_args()

    config = expand_path(args.config)
    report_dir = expand_path(args.report_dir)
    log_dir = expand_path(args.log_dir)
    plist_path = expand_path(args.plist)
    write_default_config(config)
    write_plist(plist_path, plist_payload(
        hour=max(0, min(args.hour, 23)),
        minute=max(0, min(args.minute, 59)),
        config=config,
        report_dir=report_dir,
        notify=not args.no_notify,
        log_dir=log_dir,
    ))
    events = load_launchd(plist_path) if args.load else []
    print(json.dumps({
        "mode": "install-daily-update-check",
        "label": LABEL,
        "plist": str(plist_path),
        "config": str(config),
        "reportDir": str(report_dir),
        "logDir": str(log_dir),
        "loaded": bool(args.load),
        "events": events,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
