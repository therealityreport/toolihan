import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_bug_context.py"


class CollectBugContextTest(unittest.TestCase):
    def test_non_git_directory_returns_bounded_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", tmp],
                text=True,
                capture_output=True,
                check=True,
            )

        payload = json.loads(proc.stdout)
        self.assertIs(payload["ok"], True)
        self.assertIs(payload["is_git"], False)


if __name__ == "__main__":
    unittest.main()
