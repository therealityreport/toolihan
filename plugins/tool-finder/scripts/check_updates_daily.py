#!/usr/bin/env python3
"""Daily update scanner for Tool Finder watched projects."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None

try:
    from packaging.version import Version
except ModuleNotFoundError:  # pragma: no cover - optional dependency.
    Version = None

from search_npm import fetch_detail as fetch_npm_detail
from search_npm import latest_document as latest_npm_document
from search_pypi import fetch_project as fetch_pypi_project


DEFAULT_CONFIG = {
    "roots": [
        "~/Projects",
        "~/Documents/Codex",
        "~/.agents/plugins/plugins",
        "~/.codex/plugins",
    ],
    "maxDepth": 4,
    "maxProjects": 250,
    "checks": {
        "git": True,
        "npm": True,
        "python": True,
        "homebrew": True,
        "mcp": True,
    },
    "excludeDirs": [
        ".git",
        ".hg",
        ".svn",
        ".cache",
        ".next",
        ".turbo",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        "node_modules",
        "vendor",
    ],
}

PROJECT_MARKERS = (
    ".git",
    ".codex-plugin",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "Brewfile",
    ".mcp.json",
    "mcp.json",
)

REQUIREMENT_PIN_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([A-Za-z0-9_.!+:-]+)")
REQ_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def today_slug() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def load_config(path: Path | None) -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if path and path.exists():
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        deep_update(config, loaded)
    return config


def deep_update(base: dict[str, Any], overrides: dict[str, Any]) -> None:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value


def expand_path(raw: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(raw))).resolve()


def run_command(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or f"Timed out after {timeout}s"
    return completed.returncode, completed.stdout, completed.stderr


def is_project(path: Path) -> bool:
    return any((path / marker).exists() for marker in PROJECT_MARKERS)


def discover_projects(config: dict[str, Any]) -> list[Path]:
    roots = [expand_path(root) for root in config.get("roots", [])]
    max_depth = int(config.get("maxDepth", 4))
    max_projects = int(config.get("maxProjects", 250))
    excludes = set(config.get("excludeDirs", []))
    projects: list[Path] = []
    seen: set[Path] = set()

    for root in roots:
        if not root.exists():
            continue
        root = root.resolve()
        if is_project(root) and root not in seen:
            projects.append(root)
            seen.add(root)
        for current, dirnames, _filenames in os.walk(root):
            current_path = Path(current)
            try:
                depth = len(current_path.relative_to(root).parts)
            except ValueError:
                continue
            dirnames[:] = [
                name
                for name in dirnames
                if name not in excludes and not name.startswith(".Trash")
            ]
            if depth >= max_depth:
                dirnames[:] = []
            if current_path in seen:
                dirnames[:] = []
                continue
            if current_path != root and is_project(current_path):
                projects.append(current_path)
                seen.add(current_path)
                dirnames[:] = [name for name in dirnames if name == ".codex-plugin"]
                if len(projects) >= max_projects:
                    return projects
    return projects


def finding(project: Path, kind: str, name: str, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "project": str(project),
        "kind": kind,
        "name": name,
        "message": message,
        **extra,
    }


def check_git(project: Path) -> list[dict[str, Any]]:
    if not (project / ".git").exists():
        return []
    findings: list[dict[str, Any]] = []
    code, head, _ = run_command(["git", "rev-parse", "HEAD"], cwd=project)
    if code != 0:
        return [finding(project, "git", project.name, "Could not read local Git HEAD.", severity="warning")]
    code, upstream, _ = run_command(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=project)
    if code != 0 or "/" not in upstream.strip():
        findings.append(finding(project, "git", project.name, "No upstream branch is configured.", severity="warning"))
        return findings
    remote_name, branch = upstream.strip().split("/", 1)
    code, remote_url, _ = run_command(["git", "remote", "get-url", remote_name], cwd=project)
    if code != 0:
        findings.append(finding(project, "git", project.name, f"Could not read remote URL for {remote_name}.", severity="warning"))
        return findings
    code, remote_ref, stderr = run_command(["git", "ls-remote", remote_url.strip(), f"refs/heads/{branch}"], cwd=project, timeout=45)
    if code != 0:
        findings.append(finding(project, "git", project.name, f"Could not query remote branch {upstream.strip()}.", severity="warning", detail=stderr.strip()))
        return findings
    remote_sha = remote_ref.split()[0] if remote_ref.strip() else None
    if remote_sha and remote_sha != head.strip():
        findings.append(finding(
            project,
            "git",
            upstream.strip(),
            "Remote branch differs from local HEAD.",
            severity="update",
            current=head.strip(),
            latest=remote_sha,
            command=f"git -C {project} fetch {remote_name} {branch}",
        ))
    code, status, _ = run_command(["git", "status", "--porcelain"], cwd=project)
    if code == 0 and status.strip():
        findings.append(finding(project, "git", project.name, "Local changes may affect update/rebase work.", severity="notice"))
    return findings


def check_npm(project: Path) -> list[dict[str, Any]]:
    if not (project / "package.json").exists():
        return []
    if shutil.which("npm") is None:
        return [finding(project, "npm", "npm", "npm is not available on PATH.", severity="warning")]
    code, stdout, stderr = run_command(["npm", "outdated", "--json", "--long"], cwd=project, timeout=90)
    if not stdout.strip():
        if code not in {0, 1} and stderr.strip():
            return [finding(project, "npm", "npm outdated", "npm outdated failed.", severity="warning", detail=stderr.strip()[:1000])]
        return []
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return [finding(project, "npm", "npm outdated", "npm returned non-JSON output.", severity="warning", detail=stdout[:1000])]
    findings = []
    for name, meta in payload.items():
        if not isinstance(meta, dict):
            findings.append(finding(project, "npm", name, "npm outdated returned an unexpected value shape.", severity="warning"))
            continue
        current = meta.get("current")
        latest = meta.get("latest")
        wanted = meta.get("wanted")
        if latest and current and latest != current:
            findings.append(finding(
                project,
                "npm",
                name,
                f"{name} can update from {current} to {latest}.",
                severity="update",
                current=current,
                wanted=wanted,
                latest=latest,
                command=f"npm install {name}@{latest}",
            ))
    return findings


def version_is_newer(latest: str | None, current: str | None) -> bool:
    if not latest or not current or latest == current:
        return False
    if Version is not None:
        try:
            return Version(latest) > Version(current)
        except Exception:
            pass
    return split_version(latest) > split_version(current)


def split_version(value: str) -> list[tuple[int, Any]]:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    out: list[tuple[int, Any]] = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            out.append((0, int(part)))
        else:
            out.append((1, part.lower()))
    return out


def project_python_requirements(project: Path) -> list[tuple[str, str, str]]:
    requirements: list[tuple[str, str, str]] = []
    for path in sorted(project.glob("requirements*.txt")):
        for line in safe_read_lines(path):
            match = REQUIREMENT_PIN_RE.match(line)
            if match:
                requirements.append((match.group(1), match.group(2), str(path)))
    pyproject = project / "pyproject.toml"
    if pyproject.exists() and tomllib is not None:
        try:
            payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        for spec in payload.get("project", {}).get("dependencies", []) or []:
            parsed = pinned_requirement(spec)
            if parsed:
                requirements.append((parsed[0], parsed[1], str(pyproject)))
        optional = payload.get("project", {}).get("optional-dependencies", {}) or {}
        for specs in optional.values():
            for spec in specs or []:
                parsed = pinned_requirement(spec)
                if parsed:
                    requirements.append((parsed[0], parsed[1], str(pyproject)))
        poetry_deps = payload.get("tool", {}).get("poetry", {}).get("dependencies", {}) or {}
        for name, spec in poetry_deps.items():
            if name.lower() == "python":
                continue
            if isinstance(spec, str) and spec.startswith("=="):
                requirements.append((name, spec[2:].strip(), str(pyproject)))
    return requirements


def pinned_requirement(spec: str) -> tuple[str, str] | None:
    match = REQUIREMENT_PIN_RE.match(spec)
    if match:
        return match.group(1), match.group(2)
    return None


def safe_read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def check_python(project: Path) -> list[dict[str, Any]]:
    requirements = project_python_requirements(project)
    findings = []
    for name, current, source_file in requirements:
        try:
            payload, _evidence = fetch_pypi_project(name)
        except SystemExit:
            findings.append(finding(project, "python", name, "Could not query PyPI metadata.", severity="warning", sourceFile=source_file))
            continue
        latest = (payload.get("info") or {}).get("version")
        if version_is_newer(latest, current):
            findings.append(finding(
                project,
                "python",
                name,
                f"{name} can update from {current} to {latest}.",
                severity="update",
                current=current,
                latest=latest,
                sourceFile=source_file,
                command=f"python -m pip install --dry-run --report - {name}=={latest}",
            ))
    return findings


def brewfile_entries(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in safe_read_lines(path):
        clean = line.split("#", 1)[0].strip()
        for kind in ("brew", "cask"):
            match = re.match(rf"{kind}\s+[\"']([^\"']+)[\"']", clean)
            if match:
                entries.append((kind, match.group(1)))
    return entries


def check_homebrew(project: Path) -> list[dict[str, Any]]:
    brewfile = project / "Brewfile"
    if not brewfile.exists():
        return []
    if shutil.which("brew") is None:
        return [finding(project, "homebrew", "brew", "brew is not available on PATH.", severity="warning")]
    entries = brewfile_entries(brewfile)
    if not entries:
        return []
    code, stdout, stderr = run_command(["brew", "outdated", "--json=v2"], cwd=project, timeout=120)
    if code not in {0, 1} and not stdout.strip():
        return [finding(project, "homebrew", "brew outdated", "brew outdated failed.", severity="warning", detail=stderr.strip()[:1000])]
    try:
        payload = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return [finding(project, "homebrew", "brew outdated", "brew returned non-JSON output.", severity="warning", detail=stdout[:1000])]
    formulae = {item.get("name"): item for item in payload.get("formulae", [])}
    casks = {item.get("name") or item.get("token"): item for item in payload.get("casks", [])}
    findings = []
    for kind, name in entries:
        meta = formulae.get(name) if kind == "brew" else casks.get(name)
        if not meta:
            continue
        current_versions = meta.get("installed_versions") or meta.get("installed") or []
        latest_versions = meta.get("current_version") or meta.get("latest_versions") or meta.get("version")
        findings.append(finding(
            project,
            "homebrew",
            name,
            f"{name} has a Homebrew update available.",
            severity="update",
            current=current_versions,
            latest=latest_versions,
            sourceFile=str(brewfile),
            command=f"brew upgrade {'--cask ' if kind == 'cask' else ''}{name}",
        ))
    return findings


def check_mcp(project: Path) -> list[dict[str, Any]]:
    findings = []
    for path in [project / ".mcp.json", project / "mcp.json"]:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            findings.append(finding(project, "mcp", str(path), "MCP config is not valid JSON.", severity="warning"))
            continue
        servers = payload.get("mcpServers") or payload.get("servers") or {}
        if not isinstance(servers, dict):
            continue
        for server_name, server in servers.items():
            if not isinstance(server, dict):
                continue
            command = str(server.get("command") or "")
            args = [str(value) for value in server.get("args") or []]
            findings.extend(check_mcp_server(project, path, server_name, command, args))
    return findings


def check_mcp_server(project: Path, config_path: Path, server_name: str, command: str, args: list[str]) -> list[dict[str, Any]]:
    if command.endswith("npx") or command == "npx":
        spec = first_package_arg(args)
        if not spec:
            return []
        name, version = split_npm_spec(spec)
        if not version or version == "latest":
            return [finding(project, "mcp", server_name, f"MCP npx package {name} is not pinned.", severity="notice", sourceFile=str(config_path))]
        try:
            metadata, _evidence = fetch_npm_detail(name)
            latest = latest_npm_document(metadata).get("version") or (metadata.get("dist-tags") or {}).get("latest")
        except SystemExit:
            return [finding(project, "mcp", server_name, f"Could not query npm metadata for {name}.", severity="warning", sourceFile=str(config_path))]
        if version_is_newer(latest, version):
            return [finding(project, "mcp", server_name, f"MCP package {name} can update from {version} to {latest}.", severity="update", current=version, latest=latest, sourceFile=str(config_path))]
    if command.endswith("uvx") or command == "uvx" or command.endswith("pipx") or command == "pipx":
        spec = first_package_arg(args)
        if not spec:
            return []
        name, version = split_python_spec(spec)
        if not version:
            return [finding(project, "mcp", server_name, f"MCP Python package {name} is not pinned.", severity="notice", sourceFile=str(config_path))]
        try:
            payload, _evidence = fetch_pypi_project(name)
            latest = (payload.get("info") or {}).get("version")
        except SystemExit:
            return [finding(project, "mcp", server_name, f"Could not query PyPI metadata for {name}.", severity="warning", sourceFile=str(config_path))]
        if version_is_newer(latest, version):
            return [finding(project, "mcp", server_name, f"MCP Python package {name} can update from {version} to {latest}.", severity="update", current=version, latest=latest, sourceFile=str(config_path))]
    return []


def first_package_arg(args: list[str]) -> str | None:
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in {"--package", "-p"}:
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        return arg
    return None


def split_npm_spec(spec: str) -> tuple[str, str | None]:
    if spec.startswith("@"):
        slash = spec.find("/")
        at = spec.rfind("@")
        if slash > 0 and at > slash:
            return spec[:at], spec[at + 1:]
        return spec, None
    if "@" in spec:
        name, version = spec.rsplit("@", 1)
        return name, version
    return spec, None


def split_python_spec(spec: str) -> tuple[str, str | None]:
    match = REQ_NAME_RE.match(spec)
    name = match.group(1) if match else spec
    pin = REQUIREMENT_PIN_RE.match(spec)
    return name, pin.group(2) if pin else None


def scan(config: dict[str, Any]) -> dict[str, Any]:
    projects = discover_projects(config)
    checks = config.get("checks", {})
    findings: list[dict[str, Any]] = []
    for project in projects:
        if checks.get("git", True):
            findings.extend(check_git(project))
        if checks.get("npm", True):
            findings.extend(check_npm(project))
        if checks.get("python", True):
            findings.extend(check_python(project))
        if checks.get("homebrew", True):
            findings.extend(check_homebrew(project))
        if checks.get("mcp", True):
            findings.extend(check_mcp(project))
    summary = {
        "projectsScanned": len(projects),
        "findings": len(findings),
        "updates": sum(1 for item in findings if item.get("severity") == "update"),
        "warnings": sum(1 for item in findings if item.get("severity") == "warning"),
        "notices": sum(1 for item in findings if item.get("severity") == "notice"),
    }
    return {
        "generatedAt": now_utc(),
        "summary": summary,
        "projects": [str(project) for project in projects],
        "findings": findings,
    }


def write_reports(report: dict[str, Any], report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    slug = today_slug()
    json_path = report_dir / f"update-check-{slug}.json"
    md_path = report_dir / f"update-check-{slug}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    latest_json = report_dir / "latest.json"
    latest_md = report_dir / "latest.md"
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    return json_path, md_path


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Tool Finder Daily Update Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"- Projects scanned: {summary['projectsScanned']}",
        f"- Findings: {summary['findings']}",
        f"- Updates: {summary['updates']}",
        f"- Warnings: {summary['warnings']}",
        f"- Notices: {summary['notices']}",
        "",
    ]
    if not report["findings"]:
        lines.append("No update findings.")
        lines.append("")
        return "\n".join(lines)
    current_project = None
    for item in sorted(report["findings"], key=lambda row: (row["project"], row["kind"], row["name"])):
        if item["project"] != current_project:
            current_project = item["project"]
            lines.extend(["", f"## {current_project}", ""])
        lines.append(f"- [{item.get('severity', 'notice')}] {item['kind']} `{item['name']}`: {item['message']}")
        if item.get("current") is not None or item.get("latest") is not None:
            lines.append(f"  - Current: `{item.get('current')}`")
            lines.append(f"  - Latest: `{item.get('latest')}`")
        if item.get("sourceFile"):
            lines.append(f"  - Source: `{item['sourceFile']}`")
        if item.get("command"):
            lines.append(f"  - Suggested dry-run/inspection command: `{item['command']}`")
    lines.append("")
    return "\n".join(lines)


def notify(report: dict[str, Any], md_path: Path) -> None:
    summary = report["summary"]
    if summary["findings"] == 0:
        title = "Tool Finder update check"
        message = "No update findings."
    else:
        title = "Tool Finder update findings"
        message = f"{summary['updates']} updates, {summary['warnings']} warnings, {summary['notices']} notices. Report: {md_path}"
    run_command([
        "osascript",
        "-e",
        f'display notification "{escape_osascript(message)}" with title "{escape_osascript(title)}"',
    ], timeout=10)


def escape_osascript(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="JSON config file. Missing files use built-in defaults.")
    parser.add_argument("--report-dir", default="~/.agents/tool-finder/reports", help="Directory for JSON and Markdown reports.")
    parser.add_argument("--notify", action="store_true", help="Show a macOS notification after writing the report.")
    args = parser.parse_args()

    config = load_config(expand_path(args.config) if args.config else None)
    report = scan(config)
    json_path, md_path = write_reports(report, expand_path(args.report_dir))
    if args.notify:
        notify(report, md_path)
    dump = {
        "mode": "tool-finder-daily-update-check",
        "jsonReport": str(json_path),
        "markdownReport": str(md_path),
        "summary": report["summary"],
    }
    json.dump(dump, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
