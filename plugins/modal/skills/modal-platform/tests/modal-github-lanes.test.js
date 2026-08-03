#!/usr/bin/env node
const { readFileSync, existsSync } = require("node:fs");
const path = require("node:path");

const skillRoot = path.resolve(__dirname, "..");
const referencesDir = path.join(skillRoot, "references");
const examplesDir = path.join(skillRoot, "examples");
const pluginRoot = path.resolve(skillRoot, "..", "..");

function findPluginJson(startDir) {
  let current = startDir;
  while (current !== path.dirname(current)) {
    const candidate = path.join(current, ".codex-plugin", "plugin.json");
    if (existsSync(candidate)) {
      return candidate;
    }
    current = path.dirname(current);
  }
  return null;
}

function readRelative(relativePath) {
  const fullPath = path.join(skillRoot, relativePath);
  if (!existsSync(fullPath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }
  return readFileSync(fullPath, "utf8");
}

function requireIncludes(text, needle, label) {
  if (!text.includes(needle)) {
    throw new Error(`${label} is missing ${needle}`);
  }
}

const repoIndex = readRelative("references/modal-repo-index.md");
const capabilityMatrix = readRelative("references/modal-capability-matrix.md");
const decodoPatterns = readRelative("references/modal-decodo-patterns.md");
const adjacentTools = readRelative("references/modal-adjacent-tools.md");
const p0PromptSnippets = readRelative("references/modal-p0-prompt-snippets.md");
const templates = readRelative("examples/templates.md");
const networkingSecurity = readRelative("references/modal-networking-security.md");
const decodoSkillPath = path.join(pluginRoot, "skills", "modal-decodo", "SKILL.md");
const pluginJsonPath = findPluginJson(skillRoot);
const pluginJson = pluginJsonPath ? readFileSync(pluginJsonPath, "utf8") : "";

if (!existsSync(decodoSkillPath)) {
  throw new Error("Missing first-class modal-decodo skill");
}

const decodoSkill = readFileSync(decodoSkillPath, "utf8");

const modalRepos = [
  "modal-labs/modal-client",
  "modal-labs/modal-examples",
  "modal-labs/credential-injection",
  "modal-labs/networking-demos",
  "modal-labs/ci-on-modal",
  "modal-labs/search-california",
  "modal-labs/modal-vibe",
  "modal-labs/vprox",
  "modal-labs/synchronicity",
  "modal-labs/asgiproxy",
  "modal-labs/open-batch-transcription",
  "modal-labs/browserman",
  "modal-labs/devlooper",
  "modal-labs/openai-agents-python-example",
  "modal-labs/awesome-modal",
  "modal-labs/stopwatch",
  "modal-labs/multinode-training-guide",
];

for (const repo of modalRepos) {
  requireIncludes(repoIndex, repo, "modal-repo-index.md");
}

for (const priority of ["P0", "P1", "P2"]) {
  requireIncludes(repoIndex, priority, "modal-repo-index.md");
}

const commonRepos = [
  "modal-labs/modal-examples",
  "modal-labs/credential-injection",
  "modal-labs/networking-demos",
  "modal-labs/ci-on-modal",
];

const commonCoverage = [repoIndex, templates, networkingSecurity, capabilityMatrix].join("\n");
for (const repo of commonRepos) {
  requireIncludes(commonCoverage, repo, "common Modal repo coverage");
}

const adjacentRepos = [
  "microsoft/playwright",
  "microsoft/playwright-python",
  "microsoft/playwright-mcp",
  "browser-use/browser-use",
  "scrapy/scrapy",
  "apify/crawlee-python",
  "modelcontextprotocol/python-sdk",
  "modelcontextprotocol/servers",
  "openai/openai-agents-python",
  "pydantic/pydantic-ai",
  "fastapi/fastapi",
  "encode/httpx",
  "PrefectHQ/prefect",
  "astral-sh/uv",
  "Unstructured-IO/unstructured",
];

for (const repo of adjacentRepos) {
  requireIncludes(adjacentTools, repo, "modal-adjacent-tools.md");
}

for (const heading of [
  "## Decision Tree",
  "## Browser Automation Branch",
  "## MCP And Agent Branch",
  "## Data Pipeline Branch",
]) {
  requireIncludes(adjacentTools, heading, "modal-adjacent-tools.md");
}

for (const needle of ["modal.Secret", "retries", "storage", "browser", "token"]) {
  requireIncludes(decodoPatterns, needle, "modal-decodo-patterns.md");
  requireIncludes(decodoSkill, needle, "modal-decodo/SKILL.md");
}

for (const repo of [
  "modal-client",
  "modal-examples",
  "credential-injection",
  "networking-demos",
  "ci-on-modal",
  "search-california",
]) {
  requireIncludes(p0PromptSnippets, repo, "modal-p0-prompt-snippets.md");
}

if (pluginJson) {
  const manifest = JSON.parse(pluginJson);
  if (manifest.skills !== "./skills/") {
    throw new Error('plugin.json must expose the portable "./skills/" root');
  }
}

for (const heading of [
  "CI-On-Modal Smoke Job",
  "Ingestion, Enrichment, And Endpoint Pattern",
  "Batch Artifact Job",
  "Decodo/HTTPX Scrape Worker",
]) {
  requireIncludes(templates, heading, "examples/templates.md");
}

console.log("Modal GitHub lane coverage ok.");
