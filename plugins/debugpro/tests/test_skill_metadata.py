import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class SkillMetadataTests(unittest.TestCase):
    def test_every_skill_has_complete_ui_metadata_and_explicit_policy(self) -> None:
        for skill_dir in sorted((PLUGIN_ROOT / "skills").iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            with self.subTest(skill=skill_dir.name):
                metadata_path = skill_dir / "agents" / "openai.yaml"
                self.assertTrue(metadata_path.exists())
                metadata = metadata_path.read_text(encoding="utf-8")
                self.assertIn("interface:\n", metadata)
                self.assertIn("  display_name: \"", metadata)
                self.assertIn("  short_description: \"", metadata)
                self.assertIn(f"  default_prompt: \"Use ${skill_dir.name}", metadata)
                expected = skill_dir.name == "debugpro"
                self.assertIn(
                    f"policy:\n  allow_implicit_invocation: {str(expected).lower()}\n",
                    metadata,
                )

    def test_duplicate_parallel_entrypoint_is_removed(self) -> None:
        self.assertFalse((PLUGIN_ROOT / "skills" / "debugpro-parallel-investigation").exists())
        for path in PLUGIN_ROOT.rglob("*.md"):
            self.assertNotIn("debugpro-parallel-investigation", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
