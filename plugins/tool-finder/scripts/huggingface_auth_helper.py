#!/usr/bin/env python3
"""Explain and diagnose Hugging Face auth for Tool Finder."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from typing import Any

from tool_finder_common import dump_json


WHOAMI_URL = "https://huggingface.co/api/whoami-v2"
USER_AGENT = "tool-finder/0.1 (+https://huggingface.co/docs/hub/oauth)"


def run(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=20)
    except FileNotFoundError:
        return 127, "Command not found."
    except subprocess.TimeoutExpired:
        return 124, "Command timed out."
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode, output[:4000]


def validate_token(token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        WHOAMI_URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
            return {
                "checked": True,
                "valid": True,
                "status": response.status,
                "accountType": payload.get("type"),
                "hasOrgs": bool(payload.get("orgs")),
                "rawReturned": False,
            }
    except urllib.error.HTTPError as error:
        return {
            "checked": True,
            "valid": False,
            "status": error.code,
            "rawReturned": False,
        }
    except urllib.error.URLError as error:
        return {
            "checked": True,
            "valid": False,
            "status": None,
            "reason": str(error.reason),
            "rawReturned": False,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-env", default="HF_TOKEN", help="Environment variable Tool Finder should read for Hugging Face auth.")
    parser.add_argument("--alternate-token-env", action="append", default=["HUGGING_FACE_HUB_TOKEN"], help="Alternate token env var to detect. Repeatable.")
    parser.add_argument("--validate-token", action="store_true", help="Validate the selected token with Hugging Face whoami-v2 without printing the token.")
    args = parser.parse_args()

    token = os.environ.get(args.token_env)
    alternate_present = [name for name in args.alternate_token_env if os.environ.get(name)]
    hf_cli = shutil.which("huggingface-cli") or shutil.which("hf")
    cli_status: dict[str, Any] = {
        "available": bool(hf_cli),
        "path": hf_cli,
        "authenticated": None,
        "rawStatus": None,
    }
    if hf_cli:
        status_code, status_output = run([hf_cli, "whoami"])
        cli_status["authenticated"] = status_code == 0
        cli_status["rawStatus"] = status_output if status_code != 0 else "Authenticated; account details suppressed."

    validation = {
        "checked": False,
        "valid": None,
        "rawReturned": False,
    }
    if token and args.validate_token:
        validation = validate_token(token)

    remediations: list[str] = []
    if token and (not args.validate_token or validation.get("valid")):
        state = "ready"
        reason = f"{args.token_env} is set. Tool Finder can use authenticated Hugging Face Hub requests."
        ready = True
    elif token:
        state = "invalid-token"
        reason = f"{args.token_env} is set, but validation did not confirm the token."
        ready = False
        remediations.extend([
            f"Replace {args.token_env} with a valid Hugging Face access token.",
            "Use read-only scopes unless a write workflow is explicitly needed.",
        ])
    elif alternate_present:
        state = "needs-env-export"
        reason = f"{args.token_env} is not set, but alternate Hugging Face token env vars are present."
        ready = False
        remediations.extend([
            f"Run: export {args.token_env}=${alternate_present[0]}",
            "Then rerun Tool Finder Hugging Face searches.",
        ])
    else:
        state = "optional-auth-missing"
        reason = f"{args.token_env} is not set. Public Hugging Face searches still work, but private or gated resources may be unavailable."
        ready = False
        remediations.extend([
            f"Set {args.token_env} to a Hugging Face access token for authenticated Hub access.",
            "Use a read-only token unless write access is explicitly required.",
        ])

    dump_json({
        "mode": "hugging-face-auth-helper",
        "provider": "hugging-face",
        "variant": "auth",
        "state": state,
        "ready": ready,
        "reason": reason,
        "tokenEnv": {
            "name": args.token_env,
            "present": bool(token),
            "alternatePresent": alternate_present,
            "valuePrinted": False,
        },
        "validation": validation,
        "huggingFaceCli": cli_status,
        "remediation": remediations,
        "providerStatus": {
            "provider": "hugging-face",
            "variant": "auth",
            "state": "available" if ready else "skipped",
            "searched": False,
            "skipped": not ready,
            "requiresAuth": True,
            "reason": reason,
            "remediation": remediations,
            "resultCount": 0,
        },
        "notes": [
            "This helper does not print or store tokens.",
            "Tool Finder can search public Hugging Face resources without a token.",
            "Use --validate-token to check the token against Hugging Face whoami-v2.",
        ],
    })


if __name__ == "__main__":
    main()
