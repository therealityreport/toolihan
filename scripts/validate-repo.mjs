#!/usr/bin/env node

import { existsSync, lstatSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const pluginsRoot = join(root, "plugins");
const errors = [];
const semver = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
const forbiddenDirectories = new Set([
  ".git", ".plan-work", ".pytest_cache", "__pycache__", "build", "coverage", "dist", "node_modules",
]);
const forbiddenText = [
  ["absolute macOS user path", /\/Users\/[A-Za-z0-9._-]+\//],
  ["private recovery mirror", /PLUGINS_REPO/],
  ["private TRR checkout", /(?:\$HOME|~)\/Projects\/TRR/],
  ["private project name", /THB-BBL/],
  ["private Modal profile", /admin-\d+|trr-backend-jobs/],
];
const secretPatterns = [
  ["OpenAI-style secret", /sk-[A-Za-z0-9_-]{20,}/],
  ["GitHub token", /gh[opusr]_[A-Za-z0-9]{20,}/],
  ["AWS access key", /AKIA[0-9A-Z]{16}/],
  ["private key", /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/],
];
const textExtensions = new Set([
  ".css", ".html", ".js", ".json", ".md", ".mjs", ".py", ".sh", ".svg", ".toml", ".ts", ".txt", ".yaml", ".yml",
]);
const intentionalSecurityFixtures = new Set([
  "plugins/debugpro/tests/test_evidence_redaction.py",
  "plugins/chrome-devtools/test/fixtures/redaction/sensitive/input.txt",
  "plugins/chrome-devtools/test/core/redaction.test.ts",
]);

function parseJson(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    errors.push(`${relative(root, path)}: invalid JSON (${error.message})`);
    return null;
  }
}

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && entry.name === ".git") return [];
    if (entry.isSymbolicLink()) return [path];
    return entry.isDirectory() ? [path, ...walk(path)] : [path];
  });
}

const codexMarketplacePath = join(root, ".agents", "plugins", "marketplace.json");
const codexMarketplace = parseJson(codexMarketplacePath);
if (codexMarketplace?.name !== "plugins-and-skills") errors.push("Codex marketplace name must be plugins-and-skills");
if (!Array.isArray(codexMarketplace?.plugins)) errors.push("Codex marketplace plugins must be an array");

const pluginNames = readdirSync(pluginsRoot)
  .filter((name) => statSync(join(pluginsRoot, name)).isDirectory())
  .sort();
const marketplaceNames = (codexMarketplace?.plugins ?? []).map((entry) => entry.name).sort();
if (JSON.stringify(pluginNames) !== JSON.stringify(marketplaceNames)) {
  errors.push("Codex marketplace entries must exactly match plugins/ directories");
}

for (const entry of codexMarketplace?.plugins ?? []) {
  if (entry.source?.source !== "local" || entry.source?.path !== `./plugins/${entry.name}`) {
    errors.push(`${entry.name}: marketplace source must be local ./plugins/${entry.name}`);
  }
  if (!entry.policy || !["AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"].includes(entry.policy.installation)) {
    errors.push(`${entry.name}: marketplace installation policy is missing or invalid`);
  }
  if (!entry.policy || !["ON_INSTALL", "ON_USE"].includes(entry.policy.authentication)) {
    errors.push(`${entry.name}: marketplace authentication policy is missing or invalid`);
  }
  if (!entry.category) errors.push(`${entry.name}: marketplace category is required`);
}

for (const pluginName of pluginNames) {
  const pluginRoot = join(pluginsRoot, pluginName);
  const manifestPath = join(pluginRoot, ".codex-plugin", "plugin.json");
  if (!existsSync(manifestPath)) {
    errors.push(`${pluginName}: missing .codex-plugin/plugin.json`);
    continue;
  }
  const manifest = parseJson(manifestPath);
  if (!manifest) continue;
  if (manifest.name !== pluginName) errors.push(`${pluginName}: manifest name does not match folder`);
  if (!semver.test(manifest.version ?? "")) errors.push(`${pluginName}: version is not strict semver`);
  if (!manifest.description) errors.push(`${pluginName}: description is required`);
  if (!manifest.author?.name) errors.push(`${pluginName}: author.name is required`);
  if (manifest.license !== "MIT") errors.push(`${pluginName}: public package must declare MIT`);
  for (const key of ["agents", "hooks", "upstream"]) {
    if (key in manifest) errors.push(`${pluginName}: unsupported manifest field ${key}`);
  }
  if (manifest.interface?.includes) errors.push(`${pluginName}: unsupported interface.includes field`);
  if (manifest.skills && !existsSync(join(pluginRoot, manifest.skills))) errors.push(`${pluginName}: skills path is missing`);
  if (typeof manifest.mcpServers === "string" && !existsSync(join(pluginRoot, manifest.mcpServers))) {
    errors.push(`${pluginName}: MCP manifest path is missing`);
  }
  if (manifest.apps && !existsSync(join(pluginRoot, manifest.apps))) errors.push(`${pluginName}: app manifest path is missing`);
  const prompts = manifest.interface?.defaultPrompt;
  if (prompts && (!Array.isArray(prompts) || prompts.length > 3 || prompts.some((prompt) => prompt.length > 128))) {
    errors.push(`${pluginName}: defaultPrompt must contain at most three strings of 128 characters or less`);
  }

  for (const skillPath of walk(pluginRoot).filter((path) => path.endsWith("SKILL.md"))) {
    const skill = readFileSync(skillPath, "utf8");
    const frontmatter = /^---\n([\s\S]*?)\n---/.exec(skill)?.[1] ?? "";
    if (!/^name:\s*\S+/m.test(frontmatter) || !/^description:\s*\S+/m.test(frontmatter)) {
      errors.push(`${relative(root, skillPath)}: SKILL.md needs name and description frontmatter`);
    }
  }
}

for (const path of walk(root)) {
  const rel = relative(root, path);
  const name = rel.split("/").at(-1);
  if (lstatSync(path).isSymbolicLink()) errors.push(`${rel}: symbolic links are not allowed in release packages`);
  if (statSafe(path)?.isDirectory() && forbiddenDirectories.has(name)) errors.push(`${rel}: generated/private directory is forbidden`);
  if (!statSafe(path)?.isFile()) continue;
  const dot = name.lastIndexOf(".");
  const extension = dot >= 0 ? name.slice(dot).toLowerCase() : "";
  if (!textExtensions.has(extension)) continue;
  const text = readFileSync(path, "utf8");
  if (rel !== "scripts/validate-repo.mjs") {
    for (const [label, pattern] of forbiddenText) if (pattern.test(text)) errors.push(`${rel}: contains ${label}`);
  }
  if (!intentionalSecurityFixtures.has(rel)) {
    for (const [label, pattern] of secretPatterns) if (pattern.test(text)) errors.push(`${rel}: contains possible ${label}`);
  }
}

function statSafe(path) {
  try { return statSync(path); } catch { return null; }
}

const claudeMarketplace = parseJson(join(root, ".claude-plugin", "marketplace.json"));
for (const entry of claudeMarketplace?.plugins ?? []) {
  const pluginRoot = join(root, entry.source ?? "");
  if (!existsSync(join(pluginRoot, ".claude-plugin", "plugin.json"))) {
    errors.push(`${entry.name}: Claude marketplace entry lacks a Claude manifest`);
  }
}

if (!existsSync(join(root, "LICENSE"))) errors.push("root MIT LICENSE is missing");
if (!existsSync(join(root, "catalog.json"))) errors.push("catalog.json is missing; run npm run catalog");

if (errors.length) {
  console.error(`Validation failed with ${errors.length} issue(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validated ${pluginNames.length} plugins with no release-blocking issues.`);
