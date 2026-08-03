#!/usr/bin/env python3
"""Export Tool Finder results as media-rich HTML reports."""

from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from tool_finder_common import dump_json, load_payload, result_list


PACKAGE_SOURCES = {"npm", "python", "pypi", "pips", "homebrew"}
ADOPTION_SCOPE_ORDER = [
    ("full", "Fully implement/use"),
    ("partial", "Partially integrate"),
    ("feature", "Feature to borrow"),
    ("reference", "Reference only"),
]
ADOPTION_SCOPE_ALIASES = {
    "full": "full",
    "fully": "full",
    "fully-implement": "full",
    "fully-use": "full",
    "use": "full",
    "partial": "partial",
    "partially": "partial",
    "partially-integrate": "partial",
    "integrate": "partial",
    "feature": "feature",
    "feature-only": "feature",
    "borrow": "feature",
    "reference": "reference",
    "reference-only": "reference",
}

SOURCE_CATALOG: dict[str, dict[str, str]] = {
    "runtime": {
        "label": "Runtime Tools",
        "domain": "chatgpt.com",
        "website": "https://chatgpt.com",
        "summary": "Callable tools and connector schemas available in the current Codex runtime.",
    },
    "local": {
        "label": "Local Inventory",
        "domain": "openai.com",
        "website": "https://openai.com",
        "summary": "Tools found by scanning local files and installed plugin assets.",
    },
    "skills-sh": {
        "label": "skills.sh",
        "domain": "skills.sh",
        "website": "https://skills.sh",
        "summary": "Skills discovered through the skills.sh provider.",
    },
    "github-repositories": {
        "label": "GitHub Repositories",
        "domain": "github.com",
        "website": "https://github.com/search?type=repositories",
        "summary": "Repository-level matches from GitHub search.",
    },
    "github-code": {
        "label": "GitHub Code Search",
        "domain": "github.com",
        "website": "https://github.com/search?type=code",
        "summary": "Code and configuration matches from GitHub search.",
    },
    "github": {
        "label": "GitHub",
        "domain": "github.com",
        "website": "https://github.com",
        "summary": "GitHub search results.",
    },
    "github-connector": {
        "label": "GitHub Connector",
        "domain": "github.com",
        "website": "https://github.com",
        "summary": "Callable GitHub connector tools exposed by the runtime catalog.",
    },
    "hugging-face": {
        "label": "Hugging Face Hub",
        "domain": "huggingface.co",
        "website": "https://huggingface.co",
        "summary": "Models, datasets, and Spaces from Hugging Face Hub.",
    },
    "hugging-face-connector": {
        "label": "Hugging Face Connector",
        "domain": "huggingface.co",
        "website": "https://huggingface.co",
        "summary": "Callable Hugging Face connector tools exposed by the runtime catalog.",
    },
    "npm": {
        "label": "npm",
        "domain": "npmjs.com",
        "website": "https://www.npmjs.com",
        "summary": "JavaScript and TypeScript packages from npm.",
    },
    "python": {
        "label": "Python Packages",
        "domain": "pypi.org",
        "website": "https://pypi.org",
        "summary": "Python packages from unified Python package search.",
    },
    "pypi": {
        "label": "PyPI",
        "domain": "pypi.org",
        "website": "https://pypi.org",
        "summary": "Python packages from PyPI.",
    },
    "pips": {
        "label": "pip Search",
        "domain": "pypi.org",
        "website": "https://pypi.org",
        "summary": "Python package candidates from pip-compatible search.",
    },
    "homebrew": {
        "label": "Homebrew",
        "domain": "brew.sh",
        "website": "https://brew.sh",
        "summary": "Homebrew formulae and casks.",
    },
    "package-registry-plan": {
        "label": "Package Registry Plan",
        "domain": "opencontainers.org",
        "website": "https://opencontainers.org",
        "summary": "Deferred provider coverage and registry planning notes.",
    },
}

CATEGORY_ORDER = [
    ("MCP", "MCP"),
    ("CLI", "CLI"),
    ("CONNECTORS", "CONNECTORS"),
    ("SKILLS", "SKILLS"),
    ("AGENTS", "AGENTS"),
    ("PLUGINS", "PLUGINS"),
    ("MODELS", "MODELS"),
    ("PACKAGES", "PACKAGES"),
    ("DATASETS", "DATASETS"),
    ("APPS", "APPS / SPACES"),
    ("SCRIPTS", "HOOKS / SCRIPTS"),
    ("TOOL_SCHEMAS", "TOOL SCHEMAS"),
    ("OTHER", "OTHER"),
]

REPORT_CSS = """
:root {
  color-scheme: light;
  --bg: #f6f7f9;
  --panel: #ffffff;
  --panel-soft: #f0f4f7;
  --text: #172026;
  --muted: #5c6973;
  --line: #d8e0e6;
  --accent: #0f766e;
  --accent-soft: #dff4f1;
  --warn: #a16207;
  --warn-soft: #fff7d6;
  --bad: #b42318;
  --bad-soft: #ffe7e4;
  --shadow: 0 18px 45px rgba(23, 32, 38, 0.08);
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a {
  color: var(--accent);
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
.page {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
  padding: 32px 0 56px;
}
.hero {
  display: grid;
  gap: 14px;
  padding: 30px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel);
  box-shadow: var(--shadow);
}
.hero-row,
.source-row,
.card-head,
.source-card,
.type-card {
  display: flex;
  align-items: center;
  gap: 12px;
}
.hero-icon,
.source-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: var(--panel-soft);
  padding: 6px;
}
.mini-icon {
  width: 20px;
  height: 20px;
  border-radius: 5px;
  vertical-align: middle;
}
h1,
h2,
h3 {
  margin: 0;
  line-height: 1.18;
}
h1 {
  font-size: 34px;
}
h2 {
  font-size: 22px;
  margin-bottom: 14px;
}
h3 {
  font-size: 18px;
}
p {
  margin: 0;
}
code {
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--panel-soft);
  color: #25313a;
}
.section {
  margin-top: 26px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}
.metric,
.source-card,
.type-card,
.result-card,
.status-card {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
}
.metric {
  padding: 14px;
}
.metric strong {
  display: block;
  font-size: 22px;
}
.metric span,
.muted {
  color: var(--muted);
}
.source-grid,
.type-grid,
.status-grid,
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.source-card,
.type-card {
  padding: 14px;
}
.source-card:hover,
.type-card:hover {
  text-decoration: none;
  border-color: #9fcfca;
}
.source-card strong,
.type-card strong {
  display: block;
  color: var(--text);
}
.source-card span,
.type-card span {
  display: block;
  color: var(--muted);
  font-size: 13px;
}
.category {
  margin-top: 24px;
}
.result-card {
  padding: 18px;
}
.card-head {
  justify-content: space-between;
  align-items: flex-start;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.card-title a,
.card-title span {
  font-weight: 700;
  overflow-wrap: anywhere;
}
.rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 38px;
  height: 30px;
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
}
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 24px;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--panel-soft);
  color: #25313a;
  font-size: 12px;
}
.badge.good {
  background: var(--accent-soft);
  color: var(--accent);
}
.badge.warn {
  background: var(--warn-soft);
  color: var(--warn);
}
.badge.bad {
  background: var(--bad-soft);
  color: var(--bad);
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.detail {
  padding: 10px;
  border-radius: 10px;
  background: var(--panel-soft);
}
.detail span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}
ul {
  margin: 10px 0 0;
  padding-left: 20px;
}
.status-card {
  padding: 14px;
}
.status-card h3 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.top-nav {
  margin-bottom: 18px;
}
.empty {
  padding: 16px;
  border: 1px dashed var(--line);
  border-radius: 12px;
  color: var(--muted);
}
@media (max-width: 640px) {
  .page {
    width: min(100vw - 24px, 1180px);
    padding-top: 18px;
  }
  .hero {
    padding: 20px;
  }
  h1 {
    font-size: 28px;
  }
  .card-head {
    display: grid;
  }
}
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower())
    return slug.strip("-") or "unknown"


def safe_text(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").strip()


def md_escape(value: Any) -> str:
    text = safe_text(value)
    return text.replace("|", "\\|")


def html_escape(value: Any) -> str:
    return html.escape(safe_text(value), quote=True)


def source_key_for_result(item: dict[str, Any]) -> str:
    source = str(item.get("source") or "unknown")
    provider = item.get("providerStatus") or {}
    variant = str(provider.get("variant") or "")

    if source == "skills.sh":
        return "skills-sh"
    if source == "github":
        if variant == "repositories":
            return "github-repositories"
        if variant == "code":
            return "github-code"
        return "github"
    if source in {"github-connector", "hugging-face-connector"}:
        return source
    if source == "runtime" and item.get("providerSource") == "connector-plugin":
        provider_name = slugify(provider.get("provider") or "")
        return f"{provider_name}-connector" if provider_name else "runtime"
    return slugify(source)


def source_key_for_status(status: dict[str, Any]) -> str:
    provider = str(status.get("provider") or "unknown")
    variant = str(status.get("variant") or "")
    if provider == "skills.sh":
        return "skills-sh"
    if provider == "github" and variant == "repositories":
        return "github-repositories"
    if provider == "github" and variant == "code":
        return "github-code"
    if provider in {"github", "hugging-face"} and variant == "connector":
        return f"{provider}-connector"
    return slugify(provider)


def source_meta(key: str) -> dict[str, str]:
    if key in SOURCE_CATALOG:
        return SOURCE_CATALOG[key]
    label = key.replace("-", " ").title()
    return {
        "label": label,
        "domain": "openai.com",
        "website": "https://openai.com",
        "summary": f"Results from {label}.",
    }


def favicon_url(meta: dict[str, str]) -> str:
    domain = meta.get("domain") or "openai.com"
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


def icon(meta: dict[str, str], *, size: int = 28) -> str:
    return (
        f'<img src="{html_escape(favicon_url(meta))}" width="{size}" height="{size}" '
        f'alt="{html_escape(meta.get("label", "source"))} favicon">'
    )


def icon_img(meta: dict[str, str], *, size: int = 28, class_name: str = "mini-icon") -> str:
    return (
        f'<img class="{html_escape(class_name)}" src="{html_escape(favicon_url(meta))}" '
        f'width="{size}" height="{size}" alt="{html_escape(meta.get("label", "source"))} favicon">'
    )


def html_link(url: str, label: str, *, class_name: str | None = None) -> str:
    if url.startswith(("http://", "https://")):
        class_attr = f' class="{html_escape(class_name)}"' if class_name else ""
        return f'<a{class_attr} href="{html_escape(url)}">{html_escape(label)}</a>'
    return f"<span>{html_escape(label)}</span>"


def result_link_html(item: dict[str, Any]) -> str:
    return html_link(result_url(item), safe_text(item.get("name") or "Unnamed tool"))


def badge_html(label: Any, *, tone: str = "") -> str:
    tone_class = f" {tone}" if tone else ""
    return f'<span class="badge{tone_class}">{html_escape(label)}</span>'


def status_tone(status: dict[str, Any]) -> str:
    state = str(status.get("state") or "").lower()
    if state in {"available", "queried"}:
        return "good"
    if state in {"skipped", "deferred"}:
        return "warn"
    if state == "error":
        return "bad"
    return ""


def bucket_tone(bucket: Any) -> str:
    value = str(bucket or "").lower()
    if value in {"strong", "usable"}:
        return "good"
    if value == "reject":
        return "bad"
    return "warn" if value == "reference" else ""


def detail_html(label: str, value: Any, *, code: bool = False) -> str:
    text = safe_text(value)
    if code:
        rendered = f"<code>{html_escape(text)}</code>"
    else:
        rendered = html_escape(text)
    return f'<div class="detail"><span>{html_escape(label)}</span>{rendered}</div>'


def list_html(items: list[str]) -> str:
    clean_items = [safe_text(item) for item in items if safe_text(item)]
    if not clean_items:
        return ""
    return "<ul>" + "".join(f"<li>{html_escape(item)}</li>" for item in clean_items) + "</ul>"


def html_document(title: str, body: str, *, favicon: str | None = None) -> str:
    favicon_link = f'<link rel="icon" href="{html_escape(favicon)}">' if favicon else ""
    return "\n".join([
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html_escape(title)}</title>",
        favicon_link,
        "<style>",
        REPORT_CSS,
        "</style>",
        "</head>",
        "<body>",
        '<main class="page">',
        body,
        "</main>",
        "</body>",
        "</html>",
        "",
    ])


def result_url(item: dict[str, Any]) -> str:
    location = item.get("location") or {}
    install = item.get("install") or {}
    return (
        safe_text(location.get("url"))
        or safe_text(install.get("installUrl"))
        or safe_text(location.get("localPath"))
        or safe_text(location.get("path"))
    )


def result_link(item: dict[str, Any]) -> str:
    name = safe_text(item.get("name") or "Unnamed tool")
    url = result_url(item)
    if url.startswith(("http://", "https://")):
        return f"[{md_escape(name)}]({url})"
    return md_escape(name)


def plain_source_label(item: dict[str, Any]) -> str:
    return source_meta(source_key_for_result(item))["label"]


def use_path(item: dict[str, Any]) -> str:
    install = item.get("install") or {}
    location = item.get("location") or {}
    return (
        safe_text(install.get("command"))
        or safe_text(install.get("installUrl"))
        or safe_text(location.get("url"))
        or safe_text(location.get("localPath"))
        or safe_text(location.get("path"))
        or "No direct use path recorded."
    )


def category_key(item: dict[str, Any]) -> str:
    asset_type = str(item.get("assetType") or "").lower()
    source = str(item.get("source") or "").lower()
    provider_source = str(item.get("providerSource") or "").lower()
    name = str(item.get("name") or "").lower()

    if asset_type in {"mcp", "mcp-server"} or "mcp" in name:
        return "MCP"
    if asset_type in {"cli", "command", "executable"}:
        return "CLI"
    if asset_type == "connector" or provider_source == "connector-plugin" or source.endswith("-connector"):
        return "CONNECTORS"
    if asset_type == "skill" or source == "skills.sh":
        return "SKILLS"
    if asset_type == "agent":
        return "AGENTS"
    if asset_type == "plugin":
        return "PLUGINS"
    if asset_type == "model":
        return "MODELS"
    if source in PACKAGE_SOURCES or asset_type in {"package", "library"}:
        return "PACKAGES"
    if asset_type == "dataset":
        return "DATASETS"
    if asset_type in {"app", "space"}:
        return "APPS"
    if asset_type in {"script", "hook"}:
        return "SCRIPTS"
    if asset_type == "tool-schema":
        return "TOOL_SCHEMAS"
    return "OTHER"


def category_label(category: str) -> str:
    labels = dict(CATEGORY_ORDER)
    return labels.get(category, category.replace("_", " ").title())


def has_install_path(item: dict[str, Any]) -> bool:
    install = item.get("install") or {}
    return bool(safe_text(install.get("command")) or safe_text(install.get("installUrl")))


def install_status(item: dict[str, Any]) -> str:
    return str((item.get("install") or {}).get("status") or "").lower()


def adoption_scope_key(item: dict[str, Any]) -> str:
    """Classify how much of a candidate is worth carrying into implementation."""
    action = str(item.get("recommendedAction") or "").lower()
    bucket = str(item.get("bucket") or "").lower()
    source = str(item.get("source") or "").lower()
    provider = item.get("providerStatus") or {}
    variant = str(provider.get("variant") or "").lower()
    asset_type = str(item.get("assetType") or "").lower()
    status = install_status(item)

    if bucket == "reject" or "reject" in action or "avoid" in action:
        return "reference"
    if status in {"already-available", "installed"}:
        return "full"
    if has_install_path(item) or status == "installable" or "dry-run-install" in action:
        if bucket in {"strong", "usable"} or any(term in action for term in ["use", "wire", "adopt", "implement"]):
            return "full"
        return "partial"
    if variant == "code" or source == "github-code":
        return "feature"
    if bucket == "reference" or "reference" in action:
        return "feature"
    if source == "github" and asset_type in {"repo", "repository", "plugin", "app"}:
        return "partial"
    if bucket == "strong" and any(term in action for term in ["install", "use", "wire", "adopt", "implement"]):
        return "full"
    if bucket in {"strong", "usable"}:
        return "partial"
    return "feature"


def implementation_scope(item: dict[str, Any]) -> str:
    labels = dict(ADOPTION_SCOPE_ORDER)
    return labels[adoption_scope_key(item)]


def normalize_adoption_scope(value: str) -> str:
    key = slugify(value)
    if key not in ADOPTION_SCOPE_ALIASES:
        expected = ", ".join(key for key, _label in ADOPTION_SCOPE_ORDER)
        raise ValueError(f"Unknown adoption scope '{value}'. Expected one of: {expected}.")
    return ADOPTION_SCOPE_ALIASES[key]


def filter_payload_by_scope(payload: dict[str, Any], scopes: list[str]) -> dict[str, Any]:
    if not scopes:
        return payload
    normalized = {normalize_adoption_scope(scope) for scope in scopes}
    copy = dict(payload)
    results = [item for item in result_list(payload) if adoption_scope_key(item) in normalized]
    counts = dict(copy.get("counts") or {})
    counts["results"] = len(results)
    counts["rankedResults"] = len(results)
    counts["adoptionScopeFilteredResults"] = len(results)
    counts["adoptionScopeFilter"] = len(normalized)
    copy["counts"] = counts
    copy["results"] = results
    copy["adoptionScopeFilter"] = sorted(normalized)
    return copy


def implementation_reason(item: dict[str, Any]) -> str:
    reason_values = [safe_text(reason) for reason in (item.get("reasons") or []) if safe_text(reason)]
    if item.get("rankReason"):
        return safe_text(item.get("rankReason"))
    if reason_values:
        return reason_values[0]
    return "Matched the requested tool, repository, model, or feature need."


def risk_summary(item: dict[str, Any]) -> str:
    risks = [
        safe_text(risk)
        for risk in ((item.get("safety") or {}).get("notes") or item.get("penalties") or [])
        if safe_text(risk)
    ]
    return risks[0] if risks else "No specific risk noted."


def category_slug(category: str) -> str:
    return slugify(category_label(category))


def group_results_by_source(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        grouped[source_key_for_result(item)].append(item)
    return dict(grouped)


def group_statuses_by_source(statuses: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for status in statuses:
        grouped[source_key_for_status(status)].append(status)
    return dict(grouped)


def group_results_by_category(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        grouped[category_key(item)].append(item)
    return dict(grouped)


def group_results_by_source_category(results: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for item in results:
        grouped[source_key_for_result(item)][category_key(item)].append(item)
    return {source: dict(categories) for source, categories in grouped.items()}


def report_source_keys(grouped_results: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(
        [
            source_key
            for source_key, items in grouped_results.items()
            if items
        ],
        key=lambda key: source_meta(key)["label"].lower(),
    )


def report_statuses(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        status
        for status in statuses
        if status.get("state") != "deferred"
    ]


def status_label(status: dict[str, Any]) -> str:
    provider = status.get("provider") or "unknown"
    variant = f":{status['variant']}" if status.get("variant") else ""
    state = status.get("state") or "unknown"
    return f"{provider}{variant} ({state})"


def status_table(statuses: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Provider | Results | State | Reason | Remediation |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for status in statuses:
        remediation = "<br>".join(md_escape(item) for item in (status.get("remediation") or [])[:3])
        lines.append(
            "| "
            f"{md_escape(status_label(status))} | "
            f"{md_escape(status.get('resultCount') if status.get('resultCount') is not None else '')} | "
            f"{md_escape(status.get('state') or 'unknown')} | "
            f"{md_escape(status.get('reason') or '')} | "
            f"{remediation or ''} |"
        )
    return lines


def source_card(item: dict[str, Any], meta: dict[str, str]) -> str:
    reasons = [safe_text(reason) for reason in (item.get("reasons") or []) if safe_text(reason)]
    risks = [safe_text(risk) for risk in ((item.get("safety") or {}).get("notes") or item.get("penalties") or []) if safe_text(risk)]
    capabilities = [safe_text(capability) for capability in (item.get("capabilities") or []) if safe_text(capability)]
    rank = item.get("rank", "?")
    score = item.get("score", 0)
    bucket = item.get("bucket", "reference")
    action = item.get("recommendedAction", "reference-only")
    body = [
        "<section>",
        "",
        f"### {icon(meta, size=20)} #{rank} {result_link(item)}",
        "",
        f"**Type:** `{md_escape(item.get('assetType') or 'unknown')}` "
        f"**Score:** `{score}` "
        f"**Bucket:** `{md_escape(bucket)}` "
        f"**Action:** `{md_escape(action)}`",
        "",
        f"**Use path:** `{md_escape(use_path(item))}`",
    ]
    if item.get("rankReason"):
        body.extend(["", f"**Rank reason:** {md_escape(item.get('rankReason'))}"])
    if reasons:
        body.extend(["", "**Why it matched:**"])
        body.extend(f"- {md_escape(reason)}" for reason in reasons[:4])
    if capabilities:
        body.extend(["", "**Capabilities:**"])
        body.append(" ".join(f"`{md_escape(capability)}`" for capability in capabilities[:8]))
    if risks:
        body.extend(["", "**Risk notes:**"])
        body.extend(f"- {md_escape(risk)}" for risk in risks[:3])
    body.extend(["", "</section>"])
    return "\n".join(body)


def render_source_file(
    *,
    title: str,
    query: str,
    source_key: str,
    results: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
) -> str:
    meta = source_meta(source_key)
    label = meta["label"]
    website = meta["website"]
    lines = [
        f"# {label}",
        "",
        f'<p>{icon(meta, size=42)} <a href="{html_escape(website)}">{html_escape(website)}</a></p>',
        "",
        meta["summary"],
        "",
        f"- Report: {title}",
        f"- Query: `{md_escape(query)}`",
        f"- Results: `{len(results)}`",
        f"- Source key: `{source_key}`",
        "",
        "## Provider Status",
        "",
        *status_table(statuses or [{
            "provider": source_key,
            "state": "unknown",
            "reason": "No provider status was recorded for this source.",
            "resultCount": len(results),
        }]),
        "",
        "## Top Results",
        "",
    ]
    if results:
        for item in sorted(results, key=lambda item: int(item.get("rank") or 999999)):
            lines.append(source_card(item, meta))
            lines.append("")
    else:
        lines.append("No results were returned for this source in the current run.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_tools_index(
    *,
    title: str,
    payload: dict[str, Any],
    source_files: dict[str, str],
    grouped_results: dict[str, list[dict[str, Any]]],
    grouped_statuses: dict[str, list[dict[str, Any]]],
) -> str:
    query = safe_text(payload.get("query"))
    results = result_list(payload)
    counts = payload.get("counts") or {}
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        by_category[category_key(item)].append(item)

    lines = [
        f"# {title}",
        "",
        f"Tool Finder suggestions for `{md_escape(query)}`.",
        "",
        "## Coverage",
        "",
        f"- Results: `{md_escape(counts.get('results', len(results)))}`",
        f"- Raw results: `{md_escape(counts.get('rawResults', len(results)))}`",
        f"- Skipped providers: `{md_escape(counts.get('skippedProviders', 0))}`",
        f"- Ranked results: `{md_escape(counts.get('rankedResults', len(results)))}`",
        "",
        "## Source Files",
        "",
        "| Source | Results | Provider state | File |",
        "| --- | ---: | --- | --- |",
    ]
    all_source_keys = sorted(set(grouped_results) | set(grouped_statuses), key=lambda key: source_meta(key)["label"].lower())
    for source_key in all_source_keys:
        meta = source_meta(source_key)
        states = ", ".join(sorted({safe_text(status.get("state") or "unknown") for status in grouped_statuses.get(source_key, [])}))
        source_file = source_files.get(source_key)
        file_link = f"[{md_escape(Path(source_file).name)}]({source_file})" if source_file else ""
        lines.append(
            "| "
            f"{icon(meta, size=18)} {md_escape(meta['label'])} | "
            f"{len(grouped_results.get(source_key, []))} | "
            f"{md_escape(states or 'unknown')} | "
            f"{file_link} |"
        )

    lines.extend(["", "## Suggestions By Tool Type", ""])
    for category_key_value, label in CATEGORY_ORDER:
        items = sorted(by_category.get(category_key_value, []), key=lambda item: int(item.get("rank") or 999999))
        if not items:
            continue
        lines.extend([
            f"## {label}",
            "",
            "| Rank | Source | Tool | Type | Score | Best action | Use path |",
            "| ---: | --- | --- | --- | ---: | --- | --- |",
        ])
        for item in items:
            key = source_key_for_result(item)
            meta = source_meta(key)
            lines.append(
                "| "
                f"{md_escape(item.get('rank', '?'))} | "
                f"{icon(meta, size=16)} {md_escape(meta['label'])} | "
                f"{result_link(item)} | "
                f"{md_escape(item.get('assetType') or 'unknown')} | "
                f"{md_escape(item.get('score', 0))} | "
                f"{md_escape(item.get('recommendedAction') or 'reference-only')} | "
                f"`{md_escape(use_path(item))}` |"
            )
        lines.append("")

    skipped = payload.get("skippedProviders") or []
    if skipped:
        lines.extend(["## Skipped Sources", "", *status_table(skipped), ""])
    return "\n".join(lines).rstrip() + "\n"


def render_tools_markdown(
    *,
    title: str,
    payload: dict[str, Any],
    source_files: dict[str, str] | None = None,
    type_files: dict[str, str] | None = None,
    source_type_files: dict[str, dict[str, str]] | None = None,
) -> str:
    query = safe_text(payload.get("query"))
    results = sorted(result_list(payload), key=lambda item: int(item.get("rank") or 999999))
    counts = payload.get("counts") or {}
    by_category = group_results_by_category(results)
    source_files = source_files or {}
    type_files = type_files or {}
    source_type_files = source_type_files or {}

    lines = [
        f"# {title}",
        "",
        f"Tool Finder implementation candidates for `{md_escape(query)}`.",
        "",
        "Use this file as the working shortlist for tools, repositories, models, packages, or features to implement fully, integrate partially, or borrow from.",
        "",
        "## Coverage",
        "",
        f"- Results: `{md_escape(counts.get('results', len(results)))}`",
        f"- Raw results: `{md_escape(counts.get('rawResults', len(results)))}`",
        f"- Skipped providers: `{md_escape(counts.get('skippedProviders', 0))}`",
        f"- Ranked results: `{md_escape(counts.get('rankedResults', len(results)))}`",
        "",
        "## Implementation Shortlist",
        "",
    ]

    if not results:
        lines.extend([
            "No implementation candidates were returned for this search.",
            "",
        ])
    else:
        lines.extend([
            "| Rank | Candidate | Source | Type | Consider As | Best Action | Why Consider | Use Path | Risk / Note |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for item in results:
            lines.append(
                "| "
                f"{md_escape(item.get('rank', '?'))} | "
                f"{result_link(item)} | "
                f"{md_escape(plain_source_label(item))} | "
                f"{md_escape(item.get('assetType') or 'unknown')} | "
                f"{md_escape(implementation_scope(item))} | "
                f"{md_escape(item.get('recommendedAction') or 'reference-only')} | "
                f"{md_escape(implementation_reason(item))} | "
                f"`{md_escape(use_path(item))}` | "
                f"{md_escape(risk_summary(item))} |"
            )
        lines.append("")

    lines.extend(["## Candidates By Type", ""])
    for category_key_value, label in CATEGORY_ORDER:
        items = sorted(by_category.get(category_key_value, []), key=lambda item: int(item.get("rank") or 999999))
        if not items:
            continue
        type_file = type_files.get(category_key_value)
        heading = f"### {label}"
        if type_file:
            heading += f" ([details]({type_file}))"
        lines.extend([
            heading,
            "",
            "| Rank | Candidate | Source | Consider As | Feature / Capability To Carry Forward |",
            "| ---: | --- | --- | --- | --- |",
        ])
        for item in items:
            capabilities = [safe_text(capability) for capability in (item.get("capabilities") or []) if safe_text(capability)]
            feature = "; ".join(capabilities[:3]) or implementation_reason(item)
            source_key = source_key_for_result(item)
            source_file = source_files.get(source_key)
            source_label = md_escape(plain_source_label(item))
            source_cell = f"[{source_label}]({source_file})" if source_file else source_label
            lines.append(
                "| "
                f"{md_escape(item.get('rank', '?'))} | "
                f"{result_link(item)} | "
                f"{source_cell} | "
                f"{md_escape(implementation_scope(item))} | "
                f"{md_escape(feature)} |"
            )
        lines.append("")

    by_scope: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        by_scope[adoption_scope_key(item)].append(item)
    lines.extend(["## Candidates By Adoption Scope", ""])
    for scope_key, scope_label in ADOPTION_SCOPE_ORDER:
        items = sorted(by_scope.get(scope_key, []), key=lambda item: int(item.get("rank") or 999999))
        if not items:
            continue
        lines.extend([
            f"### {scope_label}",
            "",
            "| Rank | Candidate | Source | Best Action | Use Path |",
            "| ---: | --- | --- | --- | --- |",
        ])
        for item in items:
            lines.append(
                "| "
                f"{md_escape(item.get('rank', '?'))} | "
                f"{result_link(item)} | "
                f"{md_escape(plain_source_label(item))} | "
                f"{md_escape(item.get('recommendedAction') or 'reference-only')} | "
                f"`{md_escape(use_path(item))}` |"
            )
        lines.append("")

    source_type_links = [
        f"- [{md_escape(source_meta(source_key)['label'])}: {md_escape(category_label(category))}]({path})"
        for source_key, category_paths in sorted(source_type_files.items(), key=lambda item: source_meta(item[0])["label"].lower())
        for category, path in sorted(category_paths.items(), key=lambda item: category_label(item[0]).lower())
    ]
    if source_type_links:
        lines.extend([
            "## Source / Type Detail Pages",
            "",
            *source_type_links,
            "",
        ])

    statuses = payload.get("providerStatus") if isinstance(payload.get("providerStatus"), list) else []
    if statuses:
        lines.extend([
            "## Provider Coverage",
            "",
            *status_table(report_statuses(statuses)),
            "",
        ])

    skipped = payload.get("skippedProviders") or []
    if skipped:
        lines.extend([
            "## Skipped Sources",
            "",
            *status_table(skipped),
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"


def write_tools_markdown(payload: dict[str, Any], path: Path, *, title: str | None = None) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    report_title = title or "Tool Finder Results"
    path.write_text(render_tools_markdown(title=report_title, payload=payload), encoding="utf-8")
    return {
        "format": "markdown",
        "toolsMarkdownFile": str(path),
        "filesWritten": [str(path)],
    }


def status_cards_html(statuses: list[dict[str, Any]]) -> str:
    if not statuses:
        return '<div class="empty">No provider status was recorded.</div>'
    cards: list[str] = []
    for status in statuses:
        remediation_items = [safe_text(item) for item in (status.get("remediation") or [])[:3]]
        result_count = status.get("resultCount")
        cards.append(
            "\n".join([
                '<article class="status-card">',
                "<h3>"
                f"<span>{html_escape(status_label(status))}</span>"
                f"{badge_html(status.get('state') or 'unknown', tone=status_tone(status))}"
                "</h3>",
                '<div class="detail-grid">',
                detail_html("Results", "" if result_count is None else result_count),
                detail_html("Requires auth", "yes" if status.get("requiresAuth") else "no"),
                "</div>",
                f"<p class=\"muted\">{html_escape(status.get('reason') or '')}</p>" if status.get("reason") else "",
                list_html(remediation_items),
                "</article>",
            ])
        )
    return '<div class="status-grid">' + "\n".join(cards) + "</div>"


def result_card_html(item: dict[str, Any], meta: dict[str, str], *, show_source: bool = False) -> str:
    reasons = [safe_text(reason) for reason in (item.get("reasons") or []) if safe_text(reason)]
    risks = [
        safe_text(risk)
        for risk in ((item.get("safety") or {}).get("notes") or item.get("penalties") or [])
        if safe_text(risk)
    ]
    capabilities = [safe_text(capability) for capability in (item.get("capabilities") or []) if safe_text(capability)]
    rank = item.get("rank", "?")
    score = item.get("score", 0)
    bucket = item.get("bucket", "reference")
    action = item.get("recommendedAction", "reference-only")
    asset_type = item.get("assetType") or "unknown"
    source_label = meta.get("label", item.get("source") or "unknown")
    source_bits = ""
    if show_source:
        source_bits = (
            '<div class="source-row muted">'
            f"{icon_img(meta, size=18)}"
            f"<span>{html_escape(source_label)}</span>"
            "</div>"
        )
    capability_badges = "".join(badge_html(capability) for capability in capabilities[:8])
    return "\n".join([
        '<article class="result-card">',
        '<div class="card-head">',
        '<div class="card-title">',
        f"{icon_img(meta, size=26)}",
        f"<div>{source_bits}{result_link_html(item)}</div>",
        "</div>",
        f'<span class="rank">#{html_escape(rank)}</span>',
        "</div>",
        '<div class="badges">',
        badge_html(f"Type: {asset_type}"),
        badge_html(f"Score: {score}"),
        badge_html(f"Bucket: {bucket}", tone=bucket_tone(bucket)),
        badge_html(f"Consider as: {implementation_scope(item)}"),
        badge_html(f"Action: {action}"),
        "</div>",
        '<div class="detail-grid">',
        detail_html("Use path", use_path(item), code=True),
        detail_html("Rank reason", item.get("rankReason") or "Final ranked result."),
        "</div>",
        '<div class="section">',
        "<h3>Why it matched</h3>",
        list_html(reasons[:4]) or '<p class="muted">No match reason recorded.</p>',
        "</div>",
        (
            '<div class="section"><h3>Capabilities</h3><div class="badges">'
            f"{capability_badges}"
            "</div></div>"
            if capability_badges else ""
        ),
        '<div class="section">',
        "<h3>Risk notes</h3>",
        list_html(risks[:3]) or '<p class="muted">No specific risk noted.</p>',
        "</div>",
        "</article>",
    ])


def render_source_file_html(
    *,
    title: str,
    query: str,
    source_key: str,
    results: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
) -> str:
    meta = source_meta(source_key)
    status_values = statuses or [{
        "provider": source_key,
        "state": "unknown",
        "reason": "No provider status was recorded for this source.",
        "resultCount": len(results),
    }]
    result_cards = "\n".join(
        result_card_html(item, meta)
        for item in sorted(results, key=lambda item: int(item.get("rank") or 999999))
    )
    if not result_cards:
        result_cards = '<div class="empty">No results were returned for this source in the current run.</div>'
    body = "\n".join([
        '<nav class="top-nav"><a href="../TOOLS.html">Back to TOOLS.html</a></nav>',
        '<header class="hero">',
        '<div class="hero-row">',
        f"{icon_img(meta, size=44, class_name='hero-icon')}",
        "<div>",
        f"<h1>{html_escape(meta['label'])}</h1>",
        f'<p>{html_link(meta["website"], meta["website"])}</p>',
        "</div>",
        "</div>",
        f"<p>{html_escape(meta['summary'])}</p>",
        '<div class="metrics">',
        f'<div class="metric"><strong>{len(results)}</strong><span>results</span></div>',
        f'<div class="metric"><strong>{html_escape(source_key)}</strong><span>source key</span></div>',
        f'<div class="metric"><strong>{html_escape(query)}</strong><span>query</span></div>',
        "</div>",
        "</header>",
        '<section class="section">',
        "<h2>Provider Status</h2>",
        status_cards_html(status_values),
        "</section>",
        '<section class="section">',
        "<h2>Top Results</h2>",
        '<div class="card-grid">',
        result_cards,
        "</div>",
        "</section>",
    ])
    return html_document(f"{meta['label']} - {title}", body, favicon=favicon_url(meta))


def source_summary_card_html(
    source_key: str,
    *,
    source_file: str | None,
    result_count: int,
    statuses: list[dict[str, Any]],
) -> str:
    meta = source_meta(source_key)
    states = ", ".join(sorted({safe_text(status.get("state") or "unknown") for status in statuses}))
    state_text = states or "unknown"
    href = source_file or "#"
    return "\n".join([
        f'<a class="source-card" href="{html_escape(href)}">',
        f"{icon_img(meta, size=34, class_name='source-icon')}",
        "<span>",
        f"<strong>{html_escape(meta['label'])}</strong>",
        f"<span>{result_count} results - {html_escape(state_text)}</span>",
        "</span>",
        "</a>",
    ])


def type_summary_card_html(category: str, *, type_file: str | None, result_count: int) -> str:
    label = category_label(category)
    href = type_file or "#"
    return "\n".join([
        f'<a class="type-card" href="{html_escape(href)}">',
        '<span class="rank">#</span>',
        "<span>",
        f"<strong>{html_escape(label)}</strong>",
        f"<span>{result_count} results</span>",
        "</span>",
        "</a>",
    ])


def source_type_summary_card_html(
    source_key: str,
    category: str,
    *,
    source_type_file: str | None,
    result_count: int,
) -> str:
    meta = source_meta(source_key)
    label = category_label(category)
    href = source_type_file or "#"
    return "\n".join([
        f'<a class="type-card" href="{html_escape(href)}">',
        f"{icon_img(meta, size=34, class_name='source-icon')}",
        "<span>",
        f"<strong>{html_escape(label)}</strong>",
        f"<span>{html_escape(meta['label'])} - {result_count} results</span>",
        "</span>",
        "</a>",
    ])


def render_type_file_html(
    *,
    title: str,
    query: str,
    category: str,
    results: list[dict[str, Any]],
    source_type_files: dict[str, dict[str, str]],
) -> str:
    label = category_label(category)
    by_source = group_results_by_source(results)
    source_cards = "\n".join(
        source_type_summary_card_html(
            source_key,
            category,
            source_type_file=f"../{source_type_files[source_key][category]}" if source_type_files.get(source_key, {}).get(category) else None,
            result_count=len(items),
        )
        for source_key, items in sorted(by_source.items(), key=lambda item: source_meta(item[0])["label"].lower())
    )
    result_cards = "\n".join(
        result_card_html(item, source_meta(source_key_for_result(item)), show_source=True)
        for item in sorted(results, key=lambda item: int(item.get("rank") or 999999))
    )
    body = "\n".join([
        '<nav class="top-nav"><a href="../TOOLS.html">Back to TOOLS.html</a></nav>',
        '<header class="hero">',
        '<div class="hero-row">',
        '<span class="rank">#</span>',
        "<div>",
        f"<h1>{html_escape(label)}</h1>",
        f"<p>Tool Finder {html_escape(label)} suggestions for <code>{html_escape(query)}</code>.</p>",
        "</div>",
        "</div>",
        '<div class="metrics">',
        f'<div class="metric"><strong>{len(results)}</strong><span>results</span></div>',
        f'<div class="metric"><strong>{len(by_source)}</strong><span>sources</span></div>',
        f'<div class="metric"><strong>{html_escape(category)}</strong><span>type key</span></div>',
        "</div>",
        "</header>",
        '<section class="section">',
        "<h2>Files By Source</h2>",
        '<div class="type-grid">',
        source_cards or '<div class="empty">No source/type files were generated for this tool type.</div>',
        "</div>",
        "</section>",
        '<section class="section">',
        "<h2>Results</h2>",
        '<div class="card-grid">',
        result_cards or '<div class="empty">No results were returned for this tool type.</div>',
        "</div>",
        "</section>",
    ])
    return html_document(f"{label} - {title}", body, favicon=favicon_url(source_meta("runtime")))


def render_source_type_file_html(
    *,
    title: str,
    query: str,
    source_key: str,
    category: str,
    results: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
) -> str:
    meta = source_meta(source_key)
    label = category_label(category)
    result_cards = "\n".join(
        result_card_html(item, meta)
        for item in sorted(results, key=lambda item: int(item.get("rank") or 999999))
    )
    body = "\n".join([
        '<nav class="top-nav"><a href="../../TOOLS.html">Back to TOOLS.html</a></nav>',
        '<header class="hero">',
        '<div class="hero-row">',
        f"{icon_img(meta, size=44, class_name='hero-icon')}",
        "<div>",
        f"<h1>{html_escape(meta['label'])}: {html_escape(label)}</h1>",
        f"<p>{html_escape(label)} results from {html_link(meta['website'], meta['label'])} for <code>{html_escape(query)}</code>.</p>",
        "</div>",
        "</div>",
        '<div class="metrics">',
        f'<div class="metric"><strong>{len(results)}</strong><span>results</span></div>',
        f'<div class="metric"><strong>{html_escape(source_key)}</strong><span>source key</span></div>',
        f'<div class="metric"><strong>{html_escape(category)}</strong><span>type key</span></div>',
        "</div>",
        "</header>",
        '<section class="section">',
        "<h2>Provider Status</h2>",
        status_cards_html(statuses),
        "</section>",
        '<section class="section">',
        "<h2>Results</h2>",
        '<div class="card-grid">',
        result_cards or '<div class="empty">No results were returned for this source/type pair.</div>',
        "</div>",
        "</section>",
    ])
    return html_document(f"{meta['label']} {label} - {title}", body, favicon=favicon_url(meta))


def render_tools_index_html(
    *,
    title: str,
    payload: dict[str, Any],
    source_files: dict[str, str],
    type_files: dict[str, str],
    source_type_files: dict[str, dict[str, str]],
    grouped_results: dict[str, list[dict[str, Any]]],
    grouped_statuses: dict[str, list[dict[str, Any]]],
) -> str:
    query = safe_text(payload.get("query"))
    results = result_list(payload)
    counts = payload.get("counts") or {}
    by_category = group_results_by_category(results)
    visible_statuses = report_statuses(payload.get("providerStatus") if isinstance(payload.get("providerStatus"), list) else [])

    all_source_keys = report_source_keys(grouped_results)
    source_cards = "\n".join(
        source_summary_card_html(
            source_key,
            source_file=source_files.get(source_key),
            result_count=len(grouped_results.get(source_key, [])),
            statuses=grouped_statuses.get(source_key, []),
        )
        for source_key in all_source_keys
    )
    type_cards = "\n".join(
        type_summary_card_html(
            category,
            type_file=type_files.get(category),
            result_count=len(by_category.get(category, [])),
        )
        for category, _label in CATEGORY_ORDER
        if category in by_category
    )
    source_type_cards = "\n".join(
        source_type_summary_card_html(
            source_key,
            category,
            source_type_file=source_type_files.get(source_key, {}).get(category),
            result_count=len(items),
        )
        for source_key, categories in sorted(group_results_by_source_category(results).items(), key=lambda item: source_meta(item[0])["label"].lower())
        for category, items in sorted(categories.items(), key=lambda item: category_label(item[0]).lower())
    )
    category_sections: list[str] = []
    for category_key_value, label in CATEGORY_ORDER:
        items = sorted(by_category.get(category_key_value, []), key=lambda item: int(item.get("rank") or 999999))
        if not items:
            continue
        cards = "\n".join(
            result_card_html(item, source_meta(source_key_for_result(item)), show_source=True)
            for item in items
        )
        category_sections.append(
            "\n".join([
                f'<section class="category" id="{html_escape(slugify(label))}">',
                f"<h2>{html_escape(label)}</h2>",
                '<div class="card-grid">',
                cards,
                "</div>",
                "</section>",
            ])
        )

    provider_coverage_section = ""
    if visible_statuses:
        provider_coverage_section = "\n".join([
            '<section class="section">',
            "<h2>Provider Coverage</h2>",
            status_cards_html(visible_statuses),
            "</section>",
        ])

    skipped = report_statuses(payload.get("skippedProviders") or [])
    skipped_section = ""
    if skipped:
        skipped_section = "\n".join([
            '<section class="section">',
            "<h2>Skipped Sources</h2>",
            status_cards_html(skipped),
            "</section>",
        ])

    body = "\n".join([
        '<header class="hero">',
        '<div class="hero-row">',
        f"{icon_img(source_meta('runtime'), size=44, class_name='hero-icon')}",
        "<div>",
        f"<h1>{html_escape(title)}</h1>",
        f"<p>Tool Finder suggestions for <code>{html_escape(query)}</code>.</p>",
        "</div>",
        "</div>",
        '<div class="metrics">',
        f'<div class="metric"><strong>{html_escape(counts.get("results", len(results)))}</strong><span>results</span></div>',
        f'<div class="metric"><strong>{html_escape(counts.get("rawResults", len(results)))}</strong><span>raw results</span></div>',
        f'<div class="metric"><strong>{html_escape(counts.get("skippedProviders", 0))}</strong><span>skipped providers</span></div>',
        f'<div class="metric"><strong>{html_escape(counts.get("rankedResults", len(results)))}</strong><span>ranked results</span></div>',
        "</div>",
        "</header>",
        '<section class="section">',
        "<h2>Source Files</h2>",
        '<div class="source-grid">',
        source_cards or '<div class="empty">No source files were generated.</div>',
        "</div>",
        "</section>",
        provider_coverage_section,
        '<section class="section">',
        "<h2>Type Files</h2>",
        '<div class="type-grid">',
        type_cards or '<div class="empty">No type files were generated.</div>',
        "</div>",
        "</section>",
        '<section class="section">',
        "<h2>Type / Source Files</h2>",
        '<div class="type-grid">',
        source_type_cards or '<div class="empty">No type/source files were generated.</div>',
        "</div>",
        "</section>",
        '<section class="section">',
        "<h2>Suggestions By Tool Type</h2>",
        "\n".join(category_sections) or '<div class="empty">No suggestions were returned.</div>',
        "</section>",
        skipped_section,
    ])
    return html_document(title, body, favicon=favicon_url(source_meta("runtime")))


def write_report_bundle(payload: dict[str, Any], output_dir: Path, *, title: str | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = output_dir / "sources"
    type_dir = output_dir / "types"
    source_type_dir = output_dir / "source-types"
    source_dir.mkdir(parents=True, exist_ok=True)
    type_dir.mkdir(parents=True, exist_ok=True)
    source_type_dir.mkdir(parents=True, exist_ok=True)

    report_title = title or "Tool Finder Results"
    query = safe_text(payload.get("query"))
    results = result_list(payload)
    statuses = payload.get("providerStatus") if isinstance(payload.get("providerStatus"), list) else []
    grouped_results = group_results_by_source(results)
    grouped_statuses = group_statuses_by_source(statuses)
    grouped_categories = group_results_by_category(results)
    grouped_source_categories = group_results_by_source_category(results)
    source_keys = report_source_keys(grouped_results)

    source_files: dict[str, str] = {}
    type_files: dict[str, str] = {}
    source_type_files: dict[str, dict[str, str]] = {}
    files_written: list[str] = []
    for source_key in source_keys:
        filename = f"{source_key}.html"
        path = source_dir / filename
        path.write_text(
            render_source_file_html(
                title=report_title,
                query=query,
                source_key=source_key,
                results=grouped_results.get(source_key, []),
                statuses=grouped_statuses.get(source_key, []),
            ),
            encoding="utf-8",
        )
        relative = path.relative_to(output_dir).as_posix()
        source_files[source_key] = relative
        files_written.append(str(path))

    for source_key, categories in sorted(grouped_source_categories.items(), key=lambda item: source_meta(item[0])["label"].lower()):
        source_category_dir = source_type_dir / source_key
        source_category_dir.mkdir(parents=True, exist_ok=True)
        source_type_files[source_key] = {}
        for category, items in sorted(categories.items(), key=lambda item: category_label(item[0]).lower()):
            path = source_category_dir / f"{category_slug(category)}.html"
            path.write_text(
                render_source_type_file_html(
                    title=report_title,
                    query=query,
                    source_key=source_key,
                    category=category,
                    results=items,
                    statuses=grouped_statuses.get(source_key, []),
                ),
                encoding="utf-8",
            )
            relative = path.relative_to(output_dir).as_posix()
            source_type_files[source_key][category] = relative
            files_written.append(str(path))

    for category, items in sorted(grouped_categories.items(), key=lambda item: category_label(item[0]).lower()):
        path = type_dir / f"{category_slug(category)}.html"
        path.write_text(
            render_type_file_html(
                title=report_title,
                query=query,
                category=category,
                results=items,
                source_type_files=source_type_files,
            ),
            encoding="utf-8",
        )
        relative = path.relative_to(output_dir).as_posix()
        type_files[category] = relative
        files_written.append(str(path))

    tools_path = output_dir / "TOOLS.html"
    tools_path.write_text(
        render_tools_index_html(
            title=report_title,
            payload=payload,
            source_files=source_files,
            type_files=type_files,
            source_type_files=source_type_files,
            grouped_results=grouped_results,
            grouped_statuses=grouped_statuses,
        ),
        encoding="utf-8",
    )
    files_written.insert(0, str(tools_path))

    tools_markdown_path = output_dir / "TOOLS.md"
    tools_markdown_path.write_text(
        render_tools_markdown(
            title=report_title,
            payload=payload,
            source_files=source_files,
            type_files=type_files,
            source_type_files=source_type_files,
        ),
        encoding="utf-8",
    )
    files_written.insert(1, str(tools_markdown_path))

    return {
        "format": "html+markdown",
        "outputDir": str(output_dir),
        "toolsFile": str(tools_path),
        "toolsMarkdownFile": str(tools_markdown_path),
        "indexFile": str(tools_path),
        "markdownIndexFile": str(tools_markdown_path),
        "sourceDir": str(source_dir),
        "typeDir": str(type_dir),
        "sourceTypeDir": str(source_type_dir),
        "sourceFiles": {key: str(output_dir / value) for key, value in source_files.items()},
        "typeFiles": {key: str(output_dir / value) for key, value in type_files.items()},
        "sourceTypeFiles": {
            source_key: {
                category: str(output_dir / value)
                for category, value in category_files.items()
            }
            for source_key, category_files in source_type_files.items()
        },
        "filesWritten": files_written,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="Tool Finder JSON payload, or stdin.")
    parser.add_argument("--output-dir", default="tool-finder-report", help="Directory where TOOLS.md, TOOLS.html, source, type, and source/type HTML reports are written.")
    parser.add_argument("--title", default="Tool Finder Results", help="Title for the generated HTML report.")
    parser.add_argument("--adoption-scope", action="append", default=[], help="Only export candidates matching an adoption scope: full, partial, feature, or reference. Repeatable.")
    args = parser.parse_args()

    payload = load_payload(args.input)
    if not isinstance(payload, dict):
        raise SystemExit("Expected a Tool Finder JSON object.")
    try:
        payload = filter_payload_by_scope(payload, args.adoption_scope)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    dump_json(write_report_bundle(payload, Path(args.output_dir), title=args.title))


if __name__ == "__main__":
    main()
