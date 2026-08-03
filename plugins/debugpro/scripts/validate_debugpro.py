#!/usr/bin/env python3
"""Validate the DebugPro plugin migration contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from debugpro_validation_checks import validate
from debugpro_validation_manifest import readme_explains_router
from debugpro_validation_rules import (
    MANIFESTS,
    README,
    ROOT_SKILL,
    ROUTER_AGENT,
    ROUTER_REFERENCE,
)
from debugpro_validation_text import (
    missing_agent_fields,
    missing_router_sections,
    missing_use_cases,
)
from debugpro_validation_types import Diagnostic


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def format_diagnostics(diagnostics: Sequence[Diagnostic]) -> str:
    if not diagnostics:
        return "DebugPro validation: PASS"
    lines = ["DebugPro validation: FAIL"]
    lines.extend(f"- [{item.code}] {item.path}: {item.message}" for item in diagnostics)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the DebugPro plugin migration contract.")
    parser.add_argument("--root", type=Path, default=PLUGIN_ROOT, help="DebugPro plugin root.")
    parser.add_argument("--json", action="store_true", help="Print diagnostics as JSON.")
    args = parser.parse_args(argv)

    diagnostics = validate(args.root)
    if args.json:
        print(json.dumps([item.to_dict() for item in diagnostics], indent=2, sort_keys=True))
    else:
        print(format_diagnostics(diagnostics))
    return 1 if diagnostics else 0


if __name__ == "__main__":
    sys.exit(main())
