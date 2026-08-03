#!/usr/bin/env python3
"""Compare OpenAI plugin sources, app directory cache, Codex caches, and local plugins."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


PLUGIN_MARKERS = (".app.json", ".mcp.json", ".codex-plugin/plugin.json", "plugin.json", "package.json")
GENERATED_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}


@dataclass(frozen=True)
class PluginEntry:
    key: str
    name: str
    source: str
    path: str
    version: str | None = None
    display_name: str | None = None
    kind: str | None = None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openai-repo", help="Path to a checkout of openai/plugins.")
    parser.add_argument("--app-cache-dir", default="~/.codex/cache/codex_app_directory")
    parser.add_argument("--plugin-root", default="~/.codex/plugins")
    parser.add_argument("--json-out", help="Write JSON report to this path.")
    parser.add_argument("--markdown-out", help="Write compact Markdown summary to this path.")
    parser.add_argument("--html-out", help="Write compact HTML summary to this path.")
    parser.add_argument("--format", choices=["json", "markdown", "html"], default="json")
    args = parser.parse_args()

    report = build_marketplace_diff(
        openai_repo=expand_path(args.openai_repo) if args.openai_repo else None,
        app_cache_dir=expand_path(args.app_cache_dir),
        plugin_root=expand_path(args.plugin_root),
    )

    if args.json_out:
        write_text(expand_path(args.json_out), json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.markdown_out:
        write_text(expand_path(args.markdown_out), render_markdown(report))
    if args.html_out:
        write_text(expand_path(args.html_out), render_html(report))

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.format == "markdown":
        print(render_markdown(report), end="")
    else:
        print(render_html(report), end="")


def build_marketplace_diff(openai_repo: Path | None, app_cache_dir: Path, plugin_root: Path) -> dict[str, Any]:
    sources = {
        "openaiRepo": scan_openai_repo(openai_repo) if openai_repo else [],
        "appDirectory": scan_app_directory(app_cache_dir),
        "openaiCache": scan_cache_group(plugin_root / "cache", prefix="openai-"),
        "localCache": scan_cache_group(plugin_root / "cache" / "local-plugins"),
        "localEditable": scan_local_editable(plugin_root),
    }
    keys = {source: {entry.key for entry in entries} for source, entries in sources.items()}
    union_keys = sorted(set().union(*keys.values())) if keys else []

    repo_keys = keys["openaiRepo"]
    app_keys = keys["appDirectory"]
    openai_cache_keys = keys["openaiCache"]
    local_cache_keys = keys["localCache"]
    local_editable_keys = keys["localEditable"]

    new_or_repo_only = sorted(repo_keys - app_keys - openai_cache_keys)
    missing_from_registry = sorted(repo_keys - app_keys)
    missing_from_openai_cache = sorted(repo_keys - openai_cache_keys)
    removed_or_cache_only = sorted((app_keys | openai_cache_keys) - repo_keys)
    local_cache_missing_editable = sorted(local_cache_keys - local_editable_keys)
    editable_missing_local_cache = sorted(local_editable_keys - local_cache_keys)
    version_drift = compute_version_drift(sources)

    return {
        "schemaVersion": "tool-finder.marketplace-diff.v1",
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "inputs": {
            "openaiRepo": str(openai_repo) if openai_repo else None,
            "appCacheDir": str(app_cache_dir),
            "pluginRoot": str(plugin_root),
        },
        "counts": {
            "openaiRepo": len(repo_keys),
            "appDirectory": len(app_keys),
            "openaiCache": len(openai_cache_keys),
            "localCache": len(local_cache_keys),
            "localEditable": len(local_editable_keys),
            "allDistinct": len(union_keys),
            "repoOnly": len(new_or_repo_only),
            "missingFromRegistry": len(missing_from_registry),
            "missingFromOpenAiCache": len(missing_from_openai_cache),
            "removedOrCacheOnly": len(removed_or_cache_only),
            "localCacheMissingEditable": len(local_cache_missing_editable),
            "editableMissingLocalCache": len(editable_missing_local_cache),
            "versionDrift": len(version_drift),
        },
        "diffs": {
            "new": entries_for_keys(new_or_repo_only, sources),
            "removed": entries_for_keys(removed_or_cache_only, sources),
            "updated": version_drift,
            "missing": {
                "fromRegistry": entries_for_keys(missing_from_registry, sources),
                "fromOpenAiCache": entries_for_keys(missing_from_openai_cache, sources),
            },
            "cacheDrift": {
                "localCacheMissingEditable": entries_for_keys(local_cache_missing_editable, sources),
                "editableMissingLocalCache": entries_for_keys(editable_missing_local_cache, sources),
            },
        },
        "sources": {name: [asdict(entry) for entry in entries] for name, entries in sources.items()},
    }


def scan_openai_repo(root: Path | None) -> list[PluginEntry]:
    if not root or not root.exists():
        return []
    plugin_dir = root / "plugins"
    base = plugin_dir if plugin_dir.exists() else root
    entries = []
    for child in safe_iterdir(base):
        if not child.is_dir() or child.name.startswith("."):
            continue
        meta = read_best_metadata(child)
        entries.append(entry_from_metadata(child.name, "openaiRepo", child, meta))
    return sorted_entries(entries)


def scan_app_directory(root: Path) -> list[PluginEntry]:
    entries = []
    if not root.exists():
        return entries
    for file_path in root.glob("*.json"):
        payload = read_json(file_path)
        for connector in payload.get("connectors", []) if isinstance(payload, dict) else []:
            if not isinstance(connector, dict):
                continue
            name = connector.get("name") or connector.get("id")
            if not name:
                continue
            entries.append(
                PluginEntry(
                    key=slugify(str(name)),
                    name=slugify(str(name)),
                    display_name=str(name),
                    source="appDirectory",
                    path=str(file_path),
                    version=string_or_none(connector.get("appMetadata", {}).get("version") if isinstance(connector.get("appMetadata"), dict) else None),
                    kind="connector",
                )
            )
    return dedupe_entries(entries)


def scan_cache_group(root: Path, prefix: str | None = None) -> list[PluginEntry]:
    entries = []
    if not root.exists():
        return entries
    candidates = []
    if prefix:
        for group in safe_iterdir(root):
            if group.is_dir() and group.name.startswith(prefix):
                candidates.extend(safe_iterdir(group))
    else:
        candidates.extend(safe_iterdir(root))

    for plugin in candidates:
        if not plugin.is_dir() or plugin.name in GENERATED_DIRS:
            continue
        version_dirs = [child for child in safe_iterdir(plugin) if child.is_dir() and child.name not in GENERATED_DIRS]
        if version_dirs and any(has_plugin_marker(child) for child in version_dirs):
            for version_dir in version_dirs:
                meta = read_best_metadata(version_dir)
                entries.append(entry_from_metadata(plugin.name, "localCache" if not prefix else "openaiCache", version_dir, meta, version=version_dir.name))
        elif has_plugin_marker(plugin):
            meta = read_best_metadata(plugin)
            entries.append(entry_from_metadata(plugin.name, "localCache" if not prefix else "openaiCache", plugin, meta))
    return sorted_entries(entries)


def scan_local_editable(root: Path) -> list[PluginEntry]:
    entries = []
    if not root.exists():
        return entries
    for child in safe_iterdir(root):
        if not child.is_dir() and not child.is_symlink():
            continue
        if child.name == "cache" or child.name.startswith("."):
            continue
        target = child.resolve()
        if has_plugin_marker(target):
            meta = read_best_metadata(target)
            entries.append(entry_from_metadata(child.name, "localEditable", target, meta))
    return sorted_entries(entries)


def compute_version_drift(sources: dict[str, list[PluginEntry]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, PluginEntry]] = {}
    for source_name, entries in sources.items():
        for entry in entries:
            by_key.setdefault(entry.key, {})[source_name] = entry
    drift = []
    for key, entries in sorted(by_key.items()):
        versions = {name: entry.version for name, entry in entries.items() if entry.version}
        if len(set(versions.values())) > 1:
            drift.append(
                {
                    "key": key,
                    "name": preferred_entry(entries).display_name or preferred_entry(entries).name,
                    "versions": versions,
                    "paths": {name: entry.path for name, entry in entries.items()},
                }
            )
    return drift


def entries_for_keys(keys: list[str], sources: dict[str, list[PluginEntry]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, PluginEntry]] = {}
    for source_name, entries in sources.items():
        for entry in entries:
            by_key.setdefault(entry.key, {})[source_name] = entry
    results = []
    for key in keys:
        entries = by_key.get(key, {})
        preferred = preferred_entry(entries)
        results.append(
            {
                "key": key,
                "name": preferred.display_name or preferred.name,
                "sources": sorted(entries),
                "versions": {name: entry.version for name, entry in entries.items() if entry.version},
                "paths": {name: entry.path for name, entry in entries.items()},
            }
        )
    return results


def preferred_entry(entries: dict[str, PluginEntry]) -> PluginEntry:
    for source_name in ("openaiRepo", "appDirectory", "openaiCache", "localEditable", "localCache"):
        if source_name in entries:
            return entries[source_name]
    return next(iter(entries.values()))


def read_best_metadata(root: Path) -> dict[str, Any]:
    for marker in PLUGIN_MARKERS:
        path = root / marker
        if path.exists() and path.is_file():
            payload = read_json(path)
            if isinstance(payload, dict):
                payload["_marker"] = marker
                return payload
    return {}


def entry_from_metadata(default_name: str, source: str, path: Path, meta: dict[str, Any], version: str | None = None) -> PluginEntry:
    interface = meta.get("interface") if isinstance(meta.get("interface"), dict) else {}
    display_name = meta.get("displayName") or meta.get("display_name") or meta.get("name") or interface.get("displayName")
    if not display_name and isinstance(meta.get("app"), dict):
        display_name = meta["app"].get("name")
    name = slugify(str(meta.get("name") or display_name or default_name))
    return PluginEntry(
        key=name,
        name=name,
        display_name=str(display_name) if display_name else default_name,
        source=source,
        path=str(path),
        version=version or string_or_none(meta.get("version")),
        kind=kind_from_marker(str(meta.get("_marker", ""))),
    )


def has_plugin_marker(root: Path) -> bool:
    return any((root / marker).exists() for marker in PLUGIN_MARKERS)


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Marketplace Diff",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        "| Metric | Count |",
        "|---|---:|",
    ]
    for key in [
        "openaiRepo",
        "appDirectory",
        "openaiCache",
        "localCache",
        "localEditable",
        "repoOnly",
        "missingFromRegistry",
        "missingFromOpenAiCache",
        "removedOrCacheOnly",
        "versionDrift",
    ]:
        lines.append(f"| {key} | {counts[key]} |")
    lines.extend(["", "## Top Diffs", ""])
    sections = [
        ("New", report["diffs"]["new"]),
        ("Removed", report["diffs"]["removed"]),
        ("Updated", report["diffs"]["updated"]),
        ("Missing From Registry", report["diffs"]["missing"]["fromRegistry"]),
        ("Cache Drift", report["diffs"]["cacheDrift"]["editableMissingLocalCache"]),
    ]
    for title, items in sections:
        lines.append(f"### {title}")
        if not items:
            lines.append("- None")
        else:
            for item in items[:25]:
                lines.append(f"- `{item.get('key')}`: {item.get('name', item.get('versions', {}))}")
        lines.append("")
    return "\n".join(lines)


def render_html(report: dict[str, Any]) -> str:
    counts = report["counts"]
    metric_cards = "\n".join(
        f"""<article class="card">
          <h2>{html.escape(label)}</h2>
          <p class="metric">{counts[key]}</p>
          <p class="muted">{html.escape(caption)}</p>
        </article>"""
        for label, key, caption in [
            ("Repo", "openaiRepo", "OpenAI repo entries"),
            ("Registry", "appDirectory", "App-directory entries"),
            ("Repo Only", "repoOnly", "Not in registry/cache"),
            ("Version Drift", "versionDrift", "Version mismatches"),
        ]
    )
    new_rows = render_item_rows(report["diffs"]["new"][:25], "New repo/plugin entry")
    updated_rows = render_item_rows(report["diffs"]["updated"][:25], "Version drift")
    missing_rows = render_item_rows(report["diffs"]["missing"]["fromRegistry"][:25], "Missing from registry")
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Marketplace Diff</title>
    <style>
      :root {{
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 84% 4.9%;
        --muted: 210 40% 96.1%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --border: 214.3 31.8% 91.4%;
        --primary: 222.2 47.4% 11.2%;
        --primary-foreground: 210 40% 98%;
        --destructive: 0 84.2% 60.2%;
        --warning: 38 92% 50%;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; background: hsl(var(--background)); color: hsl(var(--foreground)); }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px; }}
      h1, h2 {{ margin: 0; line-height: 1.2; }}
      h1 {{ font-size: 30px; font-weight: 700; letter-spacing: 0; }}
      h2 {{ font-size: 18px; font-weight: 650; letter-spacing: 0; }}
      .muted {{ color: hsl(var(--muted-foreground)); }}
      .grid {{ display: grid; gap: 16px; }}
      .summary {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin: 24px 0; }}
      .card, .alert {{ border: 1px solid hsl(var(--border)); border-radius: 8px; background: hsl(var(--card)); color: hsl(var(--card-foreground)); }}
      .card {{ padding: 18px; }}
      .alert {{ display: flex; gap: 12px; padding: 14px 16px; margin: 18px 0; }}
      .badge {{ display: inline-flex; align-items: center; border-radius: 999px; border: 1px solid hsl(var(--border)); padding: 2px 8px; font-size: 12px; font-weight: 650; }}
      .badge.pass {{ background: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }}
      .badge.warn {{ border-color: hsl(var(--warning)); }}
      .badge.fail {{ border-color: hsl(var(--destructive)); color: hsl(var(--destructive)); }}
      .metric {{ font-size: 28px; font-weight: 700; margin: 8px 0 2px; }}
      table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 12px; }}
      th, td {{ border-bottom: 1px solid hsl(var(--border)); padding: 10px 12px; text-align: left; vertical-align: top; }}
      th {{ background: hsl(var(--muted)); font-size: 12px; text-transform: uppercase; color: hsl(var(--muted-foreground)); }}
      code {{ background: hsl(var(--muted)); border-radius: 4px; padding: 1px 4px; }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <span class="badge pass">Generated</span>
        <h1>Marketplace Diff</h1>
        <p class="muted">Generated <code>{html.escape(report['generatedAt'])}</code> from OpenAI repo, app-directory cache, OpenAI caches, local cache, and editable local plugins.</p>
      </header>
      <section class="grid summary" aria-label="Summary">
        {metric_cards}
      </section>
      <div class="alert" role="status">
        <span class="badge warn">Notice</span>
        <span>Read-only comparison. No plugin install, removal, or update was executed.</span>
      </div>
      <section class="card"><h2>New</h2><table><thead><tr><th>Plugin</th><th>Reason</th><th>Sources</th><th>Versions</th></tr></thead><tbody>{new_rows}</tbody></table></section>
      <section class="card" style="margin-top:16px"><h2>Updated</h2><table><thead><tr><th>Plugin</th><th>Reason</th><th>Sources</th><th>Versions</th></tr></thead><tbody>{updated_rows}</tbody></table></section>
      <section class="card" style="margin-top:16px"><h2>Missing From Registry</h2><table><thead><tr><th>Plugin</th><th>Reason</th><th>Sources</th><th>Versions</th></tr></thead><tbody>{missing_rows}</tbody></table></section>
    </main>
  </body>
</html>
"""


def render_item_rows(items: list[dict[str, Any]], reason: str) -> str:
    if not items:
        return '<tr><td colspan="4" class="muted">None</td></tr>'
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(item.get('key', 'unknown')))}</code><br>{html.escape(str(item.get('name', '')))}</td>"
            f"<td>{html.escape(reason)}</td>"
            f"<td>{html.escape(', '.join(item.get('sources', [])))}</td>"
            f"<td>{html.escape(json.dumps(item.get('versions', {}), sort_keys=True))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def kind_from_marker(marker: str) -> str | None:
    if marker == ".app.json":
        return "app"
    if marker == ".mcp.json":
        return "mcp"
    if marker.endswith("plugin.json"):
        return "plugin"
    if marker == "package.json":
        return "package"
    return None


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def safe_iterdir(path: Path) -> list[Path]:
    try:
        return list(path.iterdir())
    except OSError:
        return []


def sorted_entries(entries: list[PluginEntry]) -> list[PluginEntry]:
    return sorted(dedupe_entries(entries), key=lambda entry: (entry.key, entry.source, entry.path))


def dedupe_entries(entries: list[PluginEntry]) -> list[PluginEntry]:
    by_identity: dict[tuple[str, str, str], PluginEntry] = {}
    for entry in entries:
        by_identity[(entry.key, entry.source, entry.path)] = entry
    return list(by_identity.values())


def string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
