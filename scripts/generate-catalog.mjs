#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const pluginsRoot = join(root, "plugins");
const pluginNames = readdirSync(pluginsRoot)
  .filter((name) => statSync(join(pluginsRoot, name)).isDirectory())
  .sort();

const catalog = {
  schemaVersion: 1,
  name: "plugins-and-skills",
  owner: "The Reality Report",
  repository: "https://github.com/therealityreport/plugins-and-skills",
  plugins: pluginNames.map((name) => {
    const pluginRoot = join(pluginsRoot, name);
    const manifest = JSON.parse(readFileSync(join(pluginRoot, ".codex-plugin", "plugin.json"), "utf8"));
    const skillCount = readdirRecursive(pluginRoot).filter((path) => path.endsWith("/SKILL.md")).length;
    const agentCount = existsSync(join(pluginRoot, "agents"))
      ? readdirSync(join(pluginRoot, "agents")).filter((file) => file.endsWith(".md") && file !== "README.md").length
      : 0;
    return {
      name,
      version: manifest.version,
      description: manifest.description,
      category: manifest.interface?.category ?? "Productivity",
      license: manifest.license,
      codex: true,
      claude: existsSync(join(pluginRoot, ".claude-plugin", "plugin.json")),
      skills: skillCount,
      agents: agentCount,
      path: `./plugins/${name}`,
    };
  }),
};

function readdirRecursive(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? readdirRecursive(path) : [path];
  });
}

writeFileSync(join(root, "catalog.json"), `${JSON.stringify(catalog, null, 2)}\n`);

const claudePlugins = catalog.plugins
  .filter((plugin) => plugin.claude)
  .map((plugin) => ({
    name: plugin.name,
    source: plugin.path,
    description: plugin.description,
    version: plugin.version,
    license: plugin.license,
    category: plugin.category.toLowerCase(),
  }));

const claudeMarketplace = {
  name: "plugins-and-skills",
  owner: {
    name: "The Reality Report",
    url: "https://github.com/therealityreport",
  },
  metadata: {
    description: "Open-source plugins, skills, MCP integrations, and agent workflows.",
    version: "1.0.0",
  },
  plugins: claudePlugins,
};

writeFileSync(
  join(root, ".claude-plugin", "marketplace.json"),
  `${JSON.stringify(claudeMarketplace, null, 2)}\n`,
);

console.log(`Generated catalog for ${catalog.plugins.length} plugins (${claudePlugins.length} Claude-compatible).`);
