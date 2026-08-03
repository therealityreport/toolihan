import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestIncludesTests(unittest.TestCase):
    def test_codex_manifest_is_the_only_manifest(self) -> None:
        self.assertTrue(MANIFEST.exists())
        self.assertFalse((PLUGIN_ROOT / "plugin.json").exists())

    def test_manifest_uses_current_supported_fields(self) -> None:
        manifest = load_manifest(MANIFEST)
        self.assertNotIn("agents", manifest)
        self.assertNotIn("includes", manifest.get("interface", {}))
        for field in ("privacyPolicyURL", "termsOfServiceURL"):
            value = manifest.get("interface", {}).get(field)
            self.assertTrue(value is None or value.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
