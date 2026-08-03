from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .debugpro_sync_config import EXCLUDED_NAMES, MANIFEST, PLUGIN_NAME, SyncError
    from .debugpro_sync_files import ensure_existing_destination_is_debugpro, path_strings, read_manifest
except ImportError:
    from debugpro_sync_config import EXCLUDED_NAMES, MANIFEST, PLUGIN_NAME, SyncError
    from debugpro_sync_files import ensure_existing_destination_is_debugpro, path_strings, read_manifest


def default_cache_dir(version: str) -> Path:
    return Path.home() / ".codex/plugins/cache/local-plugins" / PLUGIN_NAME / version


def ensure_distinct_paths(source: Path, destination: Path) -> None:
    if source == destination:
        raise SyncError("Refusing to sync DebugPro onto itself.")
    if source in destination.parents:
        raise SyncError("Refusing to sync into a child path.")
    if destination in source.parents:
        raise SyncError("Refusing to sync into a parent path.")


def ensure_versioned_destination(destination: Path, version: str) -> None:
    if destination.name == version and destination.parent.name == PLUGIN_NAME:
        return
    raise SyncError(f"Destination must be DebugPro {version}: {destination}")


def ensure_destination_is_safe(source: Path, destination: Path, version: str) -> None:
    source = source.resolve()
    destination = destination.resolve()
    ensure_distinct_paths(source, destination)
    if ensure_existing_destination_is_debugpro(destination):
        return
    ensure_versioned_destination(destination, version)


def plugin_version(manifest: dict, source: Path) -> str:
    if manifest.get("name") != PLUGIN_NAME:
        raise SyncError(f"Source manifest is not DebugPro: {source / MANIFEST}")
    version = str(manifest.get("version") or "").strip()
    if not version:
        raise SyncError("Source manifest does not declare a version.")
    return version


def destination_paths(args: argparse.Namespace, version: str) -> tuple[Path, list[Path]]:
    cache_dir = (args.cache_root or default_cache_dir(version)).expanduser().resolve()
    mirror_dirs = [path.expanduser().resolve() for path in args.mirror_root]
    return cache_dir, mirror_dirs


def build_plan(args: argparse.Namespace) -> dict:
    source = args.root.resolve()
    version = plugin_version(read_manifest(source), source)
    cache_dir, mirror_dirs = destination_paths(args, version)
    destinations = [cache_dir, *mirror_dirs]
    for destination in destinations:
        ensure_destination_is_safe(source, destination, version)

    local_link = None if args.skip_local_link else cache_dir.parent / "local"
    return {
        "apply": args.apply,
        "source": str(source),
        "version": version,
        "cacheDir": str(cache_dir),
        "mirrorDirs": path_strings(mirror_dirs),
        "localLink": None if local_link is None else str(local_link),
        "excludedNames": sorted(EXCLUDED_NAMES),
    }
