import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sync_debugpro_cache  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_source(root: Path) -> None:
    manifest = {"name": "debugpro", "version": "0.3.0"}
    write(root / ".codex-plugin/plugin.json", json.dumps(manifest))
    write(root / "README.md", "# DebugPro\n")
    write(root / "skills/debugpro/SKILL.md", "# Skill\n")
    write(root / ".DS_Store", "local metadata\n")
    write(root / ".tmp/report.txt", "generated\n")
    write(root / ".plugin-eval/runs/latest/report.json", "{}\n")
    write(root / "skills/debugpro/__pycache__/cached.pyc", "generated\n")


def run_main(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = sync_debugpro_cache.main(args)
    return code, output.getvalue()


class SyncDebugProCacheTests(unittest.TestCase):
    def test_dry_run_does_not_write_destinations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            cache = Path(tmp) / "cache/local-plugins/debugpro/0.3.0"
            write_source(root)

            code, output = run_main(["--root", str(root), "--cache-root", str(cache)])

            self.assertEqual(code, 0)
            self.assertIn("Dry run only", output)
            self.assertFalse(cache.exists())

    def test_apply_syncs_cache_mirror_and_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            cache = Path(tmp) / "cache/local-plugins/debugpro/0.3.0"
            mirror = Path(tmp) / "mirror/debugpro/0.3.0"
            write_source(root)

            code, _ = run_main(
                [
                    "--root",
                    str(root),
                    "--cache-root",
                    str(cache),
                    "--mirror-root",
                    str(mirror),
                    "--apply",
                ]
            )

            self.assertEqual(code, 0)
            self.assertEqual((cache / "README.md").read_text(encoding="utf-8"), "# DebugPro\n")
            self.assertEqual((mirror / "README.md").read_text(encoding="utf-8"), "# DebugPro\n")
            self.assertEqual(
                (cache / ".codex-plugin/plugin.json").read_text(encoding="utf-8"),
                (root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"),
            )
            self.assertFalse((cache / ".DS_Store").exists())
            self.assertFalse((cache / ".tmp").exists())
            self.assertFalse((cache / ".plugin-eval/runs").exists())
            self.assertFalse((cache / "skills/debugpro/__pycache__").exists())
            self.assertTrue((cache.parent / "local").is_symlink())
            self.assertEqual((cache.parent / "local").resolve(), cache.resolve())

    def test_refuses_non_debugpro_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            cache = Path(tmp) / "cache/local-plugins/debugpro/0.3.0"
            write_source(root)
            write(cache / ".codex-plugin/plugin.json", json.dumps({"name": "other", "version": "0.3.0"}))

            code, _ = run_main(["--root", str(root), "--cache-root", str(cache), "--apply"])

            self.assertEqual(code, 1)
            self.assertEqual(
                json.loads((cache / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["name"],
                "other",
            )


if __name__ == "__main__":
    unittest.main()
