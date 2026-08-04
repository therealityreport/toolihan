# Plugins & Skills

An open-source marketplace of Codex plugins, Agent Skills, MCP integrations, and reusable agent workflows maintained by [The Reality Report](https://github.com/therealityreport).

This repository contains clean distribution packages. It does not contain local runtime caches, private recovery snapshots, credentials, customer data, or proprietary project plugins.

## Install in Codex

Add the GitHub marketplace once:

```bash
codex plugin marketplace add therealityreport/plugins-and-skills
```

Then install any plugin:

```bash
codex plugin add debugpro@plugins-and-skills
codex plugin add chrome-devtools@plugins-and-skills
codex plugin add tool-finder@plugins-and-skills
```

See the complete machine-readable catalog in [`catalog.json`](catalog.json).

For the application-focused collection with 35 standalone skills for skills.sh
and seven dedicated Codex plugin cards, see
[`therealityreport/app-skills`](https://github.com/therealityreport/app-skills):

```bash
codex plugin marketplace add therealityreport/app-skills
npx skills add therealityreport/app-skills
```

## Install in Claude Code

The plugins that include a `.claude-plugin/plugin.json` manifest are also listed in the Claude marketplace:

```text
/plugin marketplace add therealityreport/plugins-and-skills
/plugin install chrome-devtools@plugins-and-skills
```

Codex-only packages remain visible in this repository but are omitted from the Claude marketplace manifest.

## Included plugins

| Plugin | What it does | Codex | Claude |
| --- | --- | :---: | :---: |
| `chrome-devtools` | Browser runtime, network, performance, accessibility, and redacted evidence workflows | Yes | Yes |
| `codex-improve` | Evidence-backed codebase audits, plans, execution, and verification | Yes | — |
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
| `vintone-studio` | Copy-first planning and runbooks for VINTONE Photoshop workflows | Yes | Yes |

## Repository structure

```text
.agents/plugins/marketplace.json   Codex marketplace
.claude-plugin/marketplace.json    Claude Code marketplace
catalog.json                       Generated public catalog
plugins/<plugin-name>/             Installable plugin packages
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

See [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

The first-party code in this repository is released under the [MIT License](LICENSE). Third-party products, services, trademarks, and referenced materials retain their respective ownership and terms.
