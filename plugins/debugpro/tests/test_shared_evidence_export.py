import unittest

from scripts.export_shared_evidence import export_shared_evidence
from scripts.validate_shared_evidence import validate


class SharedEvidenceExportTests(unittest.TestCase):
    def test_exports_debugpro_findings(self) -> None:
        packages = export_shared_evidence(
            {
                "runId": "dbg-run",
                "findings": [
                    {
                        "id": "root-cause-1",
                        "severity": "high",
                        "claim": "Route ownership token is rejected by the active session.",
                        "path": "src/router.ts",
                        "line": 44,
                        "nextStep": "Capture the current session id before retrying.",
                    }
                ],
            }
        )

        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0]["sourcePlugin"], "debugpro")
        self.assertEqual(packages[0]["affectedFiles"], ["src/router.ts"])
        self.assertEqual(validate(packages[0]), [])


if __name__ == "__main__":
    unittest.main()
