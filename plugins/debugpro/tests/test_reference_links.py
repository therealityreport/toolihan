import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_skill_links  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ReferenceLinksTests(unittest.TestCase):
    def test_link_checker_catches_missing_local_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "skills/debugpro/SKILL.md",
                "Use `references/missing.md` before `references/present.md`.\n",
            )
            write(root / "skills/debugpro/references/present.md", "# Present\n")

            issues = check_skill_links.check_links(root)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].target, "references/missing.md")

    def test_live_debugpro_local_references_resolve(self) -> None:
        issues = check_skill_links.check_links(PLUGIN_ROOT)
        details = "\n".join(
            f"{issue.source}:{issue.line}: {issue.target}: {issue.message}" for issue in issues
        )
        self.assertEqual(issues, [], details)


if __name__ == "__main__":
    unittest.main()
