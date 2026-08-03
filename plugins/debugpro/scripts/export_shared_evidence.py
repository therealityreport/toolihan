#!/usr/bin/env python3
"""Export DebugPro findings as shared-evidence.v1 packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .shared_evidence_export_core import export_shared_evidence
    from .validate_shared_evidence import validate
except ImportError:
    from shared_evidence_export_core import export_shared_evidence
    from validate_shared_evidence import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Findings JSON file.")
    parser.add_argument("--output", type=Path, help="Output JSON/JSONL path. Defaults to stdout.")
    parser.add_argument("--run-id", help="Override runId.")
    parser.add_argument("--format", choices=["json", "jsonl"], default="json")
    args = parser.parse_args(argv)

    packages = export_shared_evidence(json.loads(args.input.read_text(encoding="utf-8")), run_id=args.run_id)
    diagnostics = []
    for index, package in enumerate(packages):
        diagnostics.extend(f"package[{index}]: {item}" for item in validate(package))
    if diagnostics:
        for diagnostic in diagnostics:
            print(f"shared-evidence-export: {diagnostic}", file=sys.stderr)
        return 1

    text = format_packages(packages, args.format)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


def format_packages(packages: list[dict[str, Any]], output_format: str) -> str:
    if output_format == "jsonl":
        return "\n".join(json.dumps(package) for package in packages) + "\n"
    return json.dumps(packages, indent=2) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
