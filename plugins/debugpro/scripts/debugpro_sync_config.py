from __future__ import annotations

from pathlib import Path


PLUGIN_NAME = "debugpro"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(".codex-plugin/plugin.json")
EXCLUDED_NAMES = frozenset(
    {
        ".DS_Store",
        ".git",
        ".pytest_cache",
        ".tmp",
        "__pycache__",
        "node_modules",
    }
)


class SyncError(RuntimeError):
    """Unsafe DebugPro sync request."""
