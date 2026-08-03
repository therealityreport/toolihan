import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_shared_evidence  # noqa: E402


class SharedEvidenceTests(unittest.TestCase):
    def test_shared_evidence_example_is_valid(self) -> None:
        example = json.loads(
            (PLUGIN_ROOT / "skills/debugpro/references/shared-evidence.v1.example.json").read_text()
        )

        self.assertEqual(validate_shared_evidence.validate(example), [])

    def test_shared_evidence_requires_sourced_evidence(self) -> None:
        invalid = {
            "runId": "run",
            "sourcePlugin": "debugpro",
            "findingId": "DBG-001",
            "severity": "high",
            "claim": "claim",
            "evidence": [],
            "affectedFiles": [],
            "recommendedNextStep": "next",
            "status": "open",
        }

        self.assertIn("evidence must be a non-empty array", validate_shared_evidence.validate(invalid))


if __name__ == "__main__":
    unittest.main()
