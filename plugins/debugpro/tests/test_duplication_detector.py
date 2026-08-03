import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_debugpro_duplication  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_shared_references(root: Path) -> None:
    for relative in check_debugpro_duplication.SHARED_REFERENCES:
        write(root / relative, "# Shared\n")


class DuplicationDetectorTests(unittest.TestCase):
    def test_repeated_long_skill_bullet_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_shared_references(root)
            repeated = (
                "- Stop before destructive cleanup, global config edits, "
                "production mutation, credential changes, or expensive actions.\n"
            )
            for name in ("debugpro-a", "debugpro-b", "debugpro-c"):
                write(root / "skills" / name / "SKILL.md", repeated)

            issues = check_debugpro_duplication.check_duplication(root)

        codes = {issue.code for issue in issues}
        self.assertIn("repeated_long_bullet", codes)

    def test_missing_contract_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_shared_references(root)
            write(root / "skills/debugpro-team/SKILL.md", "# Team\n")

            issues = check_debugpro_duplication.check_duplication(root)

        codes = {issue.code for issue in issues}
        self.assertIn("missing_parallel_contract_link", codes)

    def test_live_debugpro_has_no_duplication_findings(self) -> None:
        issues = check_debugpro_duplication.check_duplication(PLUGIN_ROOT)
        details = "\n".join(f"{issue.code}: {issue.path}: {issue.message}" for issue in issues)
        self.assertEqual(issues, [], details)


if __name__ == "__main__":
    unittest.main()
