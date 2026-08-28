# Toolihan

Toolihan is the single public home for our Codex and Claude plugins, standalone
Agent Skills, MCP integrations, and MCP Apps. The repository is maintained by
[The Reality Report](https://github.com/therealityreport) for other creators to
install, inspect, improve, and reuse.

This repository contains clean distribution packages. It does not contain local
runtime caches, private recovery snapshots, credentials, customer data, or
project-specific proprietary plugins.

## Install in Codex

Add the marketplace once:

```bash
codex plugin marketplace add therealityreport/toolihan
```

Then install any plugin:

```bash
codex plugin add debugpro@toolihan
codex plugin add chrome-devtools@toolihan
codex plugin add context7@toolihan
```

See the complete machine-readable inventory in [`catalog.json`](catalog.json).

## Install standalone skills

All standalone skills are available from this same repository:

```bash
npx skills add therealityreport/toolihan
npx skills add therealityreport/toolihan --skill context7-docs
```

“App Skills” is a collection within Toolihan, not a separate project or
repository. Its machine-readable membership is in
[`collections/app-skills.json`](collections/app-skills.json). It currently
groups skills for Chrome DevTools, Context7, Decodo, Envato to R2, Modal,
Supabase, and VINTONE Studio. Future app families such as Stripe belong in this
collection when their plugins are added.

## MCP Apps

Hosted MCP Apps and their connection details are listed in
[`mcp-apps.json`](mcp-apps.json).

| MCP App | Public MCP URL | Health check |
| --- | --- | --- |
| PDFx | `https://pdfx.hulibrands.com/mcp` | `https://pdfx.hulibrands.com/healthz` |
| Docs | `https://docs.hulibrands.com/mcp` | `https://docs.hulibrands.com/api/health` |
| Supabase | Connector-managed; no repository-owned MCP URL | Connector-managed |

The PDFx and Docs endpoints were live-verified on August 28, 2026. A normal
browser `GET` to an MCP protocol endpoint may return `405` or `406`; use an MCP
client for the protocol connection and the health URL for a simple status check.

## Install in Claude Code

Plugins with a `.claude-plugin/plugin.json` manifest are also listed in the
Claude marketplace:

```text
/plugin marketplace add therealityreport/toolihan
/plugin install chrome-devtools@toolihan
```

Codex-only packages remain visible in this repository but are omitted from the
Claude marketplace manifest.

## Included plugins

| Plugin | What it does | Codex | Claude |
| --- | --- | :---: | :---: |
| `chrome-devtools` | Browser runtime, network, performance, accessibility, and evidence workflows | Yes | Yes |
| `codex-improve` | Evidence-backed codebase audits, plans, execution, and verification | Yes | — |
| `context7` | Current library and SDK documentation through Context7 | Yes | — |
| `debugpro` | Root-cause-first debugging and evidence routing | Yes | — |
| `decodo` | Decodo scraping, proxy, MCP, and SDK workflows | Yes | Yes |
| `envato-r2` | Operator-approved Envato asset download and Cloudflare R2 delivery | Yes | Yes |
| `infographic-docs` | Multi-page HTML explainers and community pulse documents | Yes | Yes |
| `laws-of-ux` | Frontend audits against the 30 Laws of UX | Yes | Yes |
| `mcp-app-builder` | Scaffolding and validation for MCP Apps and ChatGPT Apps | Yes | Yes |
| `mermaid-png` | Mermaid diagram rendering to PNG or SVG | Yes | Yes |
| `modal` | Modal architecture, implementation, deployment, and operations guidance | Yes | — |
| `supabase-fullstack` | Connector-aware Supabase security, performance, and full-stack workflows | Yes | Yes |
| `tool-finder` | Tool, skill, plugin, MCP, CLI, and package discovery | Yes | Yes |
| `universal-debugger` | Cross-codebase debugging orchestration | Yes | Yes |
| `vintone-studio` | Planning and runbooks for VINTONE Photoshop workflows | Yes | Yes |

## Repository structure

```text
.agents/plugins/marketplace.json   Codex marketplace
.claude-plugin/marketplace.json    Claude Code marketplace
catalog.json                       Generated plugin catalog
collections/                       Curated views such as App Skills
mcp-apps.json                      Hosted MCP App connection registry
plugins/<plugin-name>/             Installable plugin packages
skills/<skill-name>/               Standalone Agent Skills
scripts/                           Catalog and validation tools
```

## Safety and privacy

- Secrets and account credentials are never committed.
- External-service plugins use environment variables or the provider's normal authentication flow.
- Live browsing, scraping, downloads, deployments, and writes remain subject to provider terms and user authorization.
- Project-specific proprietary plugins are deliberately excluded.

Run the release checks before every push:

```bash
npm run catalog
npm test
```

See [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

First-party code in this repository is released under the [MIT License](LICENSE).
Third-party products, services, trademarks, and referenced materials retain
their respective ownership and terms.
