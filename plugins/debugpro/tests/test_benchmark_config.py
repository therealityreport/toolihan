import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class BenchmarkConfigTests(unittest.TestCase):
    def test_benchmark_uses_real_fixtures_and_machine_checked_results(self) -> None:
        config = json.loads((PLUGIN_ROOT / ".plugin-eval" / "benchmark.json").read_text(encoding="utf-8"))
        self.assertEqual(config["workspace"]["sourcePath"], ".plugin-eval/fixtures")
        self.assertIn("python3 verify_diagnosis.py", config["verifiers"]["commands"])
        self.assertGreaterEqual(len(config["scenarios"]), 3)
        for scenario in config["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertIn(".plugin-eval-result.json", scenario["userInput"])
                self.assertTrue((PLUGIN_ROOT / ".plugin-eval" / "fixtures" / scenario["id"]).is_dir())

    def test_verifier_rejects_fixture_edits(self) -> None:
        source = PLUGIN_ROOT / ".plugin-eval" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixtures"
            shutil.copytree(source, workspace)
            (workspace / ".plugin-eval-result.json").write_text(
                json.dumps(
                    {
                        "scenario": "browser-runtime",
                        "primaryRoute": "debugpro-browser-runtime-proof",
                        "rootCauseCode": "missing-browser-script",
                        "evidence": [
                            "index.html requests /assets/app.js",
                            "server.log records /assets/app.js 404",
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (workspace / "browser-runtime" / "index.html").write_text("fixed", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "verify_diagnosis.py"],
                cwd=workspace,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
