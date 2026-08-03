#!/usr/bin/env python3
"""Validate shared-evidence.v1.json packages for DebugPro and Plan Grader."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .shared_evidence_validation_core import validate
    from .shared_evidence_validation_schema import load_json
except ImportError:
    from shared_evidence_validation_core import validate
    from shared_evidence_validation_schema import load_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to shared-evidence JSON.")
    parser.add_argument("--json", action="store_true", help="Print diagnostics as JSON.")
    args = parser.parse_args(argv)

    diagnostics = validate(load_json(args.path))
    if args.json:
        print(json.dumps({"ok": not diagnostics, "diagnostics": diagnostics}, indent=2))
    elif diagnostics:
        print("shared-evidence: FAIL")
        for diagnostic in diagnostics:
            print(f"- {diagnostic}")
    else:
        print(f"shared-evidence: OK {args.path}")
    return 1 if diagnostics else 0


if __name__ == "__main__":
    sys.exit(main())
