#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


root = Path.cwd()
result_path = root / ".plugin-eval-result.json"
if not result_path.exists():
    fail("missing .plugin-eval-result.json")
result = json.loads(result_path.read_text(encoding="utf-8"))
contracts = json.loads((root / "contracts.json").read_text(encoding="utf-8"))
scenario = result.get("scenario")
contract = contracts.get(scenario)
if contract is None:
    fail(f"unknown scenario: {scenario!r}")
for field in ("primaryRoute", "rootCauseCode"):
    if result.get(field) != contract[field]:
        fail(f"wrong {field}: {result.get(field)!r}")
evidence = "\n".join(str(item) for item in result.get("evidence") or []).lower()
for term in contract["evidenceTerms"]:
    if term.lower() not in evidence:
        fail(f"evidence is missing {term!r}")
for relative_path, expected_digest in contract["files"].items():
    path = root / relative_path
    if not path.is_file():
        fail(f"fixture file is missing: {relative_path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_digest:
        fail(f"fixture file changed: {relative_path}")
