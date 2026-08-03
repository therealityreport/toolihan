from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable

try:
    from .debugpro_sync_config import EXCLUDED_NAMES, MANIFEST, PLUGIN_NAME, SyncError
except ImportError:
    from debugpro_sync_config import EXCLUDED_NAMES, MANIFEST, PLUGIN_NAME, SyncError


def read_manifest(root: Path) -> dict:
    manifest_path = root / MANIFEST
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncError(f"Missing manifest: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise SyncError(f"Invalid manifest JSON: {manifest_path}: {exc}") from exc

def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def ignore_names(directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in EXCLUDED_NAMES}
    if Path(directory).name == ".plugin-eval" and "runs" in names:
        ignored.add("runs")
    return ignored


def sync_tree(source: Path, destination: Path) -> None:
    remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=ignore_names)


def maybe_refresh_local_link(cache_dir: Path, *, apply: bool, skip: bool) -> Path | None:
    if skip:
        return None
    local_link = cache_dir.parent / "local"
    if not apply:
        return local_link
    remove_path(local_link)
    local_link.symlink_to(cache_dir.resolve(), target_is_directory=True)
    return local_link


def path_strings(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths]


def existing_destination_manifest(destination: Path) -> dict | None:
    for relative_path in (MANIFEST, Path("plugin.json")):
        manifest_path = destination / relative_path
        if destination.exists() and manifest_path.exists():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
    return None


def ensure_existing_destination_is_debugpro(destination: Path) -> bool:
    manifest = existing_destination_manifest(destination)
    if manifest is None:
        return False
    if manifest.get("name") != PLUGIN_NAME:
        raise SyncError(f"Destination is not a DebugPro package: {destination}")
    return True
