#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import os from "node:os";
import path from "node:path";

function usage() {
  return [
    "Usage:",
    "  node scripts/check_codex_local_app.mjs --plugin /path/to/plugin [--cache /path/to/cache] [--id plugin-id] [--json]",
  ].join("\n");
}

function readValue(tokens, flag) {
  const value = tokens.shift();
  if (!value || value.startsWith("--")) {
    throw new Error("Expected a value after " + flag);
  }
  return value;
}

function parseArgs(argv) {
  const args = { plugin: null, cache: null, id: null, json: false };
  const tokens = [...argv];

  while (tokens.length > 0) {
    const token = tokens.shift();
    if (token === "--plugin") {
      args.plugin = readValue(tokens, token);
      continue;
    }
    if (token === "--cache") {
      args.cache = readValue(tokens, token);
      continue;
    }
    if (token === "--id") {
      args.id = readValue(tokens, token);
      continue;
    }
    if (token === "--json") {
      args.json = true;
      continue;
    }
    if (token === "--help" || token === "-h") {
      console.log(usage());
      process.exit(0);
    }
    throw new Error("Unknown argument: " + token);
  }

  if (!args.plugin) {
    throw new Error("Missing required --plugin.\n\n" + usage());
  }

  return args;
}

function readJson(filePath, errors) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    errors.push(path.basename(filePath) + " is not valid JSON: " + error.message);
    return null;
  }
}

function collectFiles(root, relativeDir = "") {
  const dir = path.join(root, relativeDir);
  if (!existsSync(dir)) {
    return [];
  }

  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".DS_Store") {
      continue;
    }
    const relativePath = path.join(relativeDir, entry.name);
    const fullPath = path.join(root, relativePath);
    if (entry.isDirectory()) {
      files.push(...collectFiles(root, relativePath));
      continue;
    }
    if (entry.isFile()) {
      const stat = statSync(fullPath);
      files.push({ relativePath, size: stat.size, mtimeMs: Math.trunc(stat.mtimeMs) });
    }
  }
  return files.sort((a, b) => a.relativePath.localeCompare(b.relativePath));
}

function treeHash(root) {
  const hash = createHash("sha256");
  for (const file of collectFiles(root)) {
    hash.update(file.relativePath);
    hash.update("\0");
    hash.update(String(file.size));
    hash.update("\0");
    hash.update(createHash("sha256").update(readFileSync(path.join(root, file.relativePath))).digest("hex"));
    hash.update("\0");
  }
  return hash.digest("hex");
}

function configContainsId(configPath, pluginId) {
  if (!existsSync(configPath)) {
    return "missing-config";
  }
  const text = readFileSync(configPath, "utf8");
  return text.includes(pluginId) ? "present" : "missing-id";
}

function printText(result) {
  console.log("Codex local app check");
  console.log("- plugin: " + result.plugin.status + " (" + result.plugin.path + ")");
  console.log("- manifest: " + result.manifest.status + " (" + result.manifest.path + ")");
  console.log("- id: " + result.id);
  console.log("- config: " + result.config.status + " (" + result.config.path + ")");
  if (result.cache) {
    console.log("- cache: " + result.cache.status + " (" + result.cache.path + ")");
    console.log("- source/cache: " + result.cache.drift);
  }
  for (const warning of result.warnings) {
    console.log("- warning: " + warning);
  }
  for (const error of result.errors) {
    console.log("- error: " + error);
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const pluginPath = path.resolve(args.plugin);
  const errors = [];
  const warnings = [];
  const result = {
    ok: false,
    id: args.id || null,
    plugin: { path: pluginPath, status: "missing" },
    manifest: { path: path.join(pluginPath, ".codex-plugin", "plugin.json"), status: "missing" },
    config: { path: path.join(os.homedir(), ".codex", "config.toml"), status: "unchecked" },
    cache: null,
    warnings,
    errors,
  };

  if (!existsSync(pluginPath) || !statSync(pluginPath).isDirectory()) {
    errors.push("Plugin path does not exist or is not a directory");
  } else {
    result.plugin.status = "present";
  }

  let manifest = null;
  if (existsSync(result.manifest.path) && statSync(result.manifest.path).isFile()) {
    result.manifest.status = "present";
    manifest = readJson(result.manifest.path, errors);
  } else {
    errors.push("Missing .codex-plugin/plugin.json");
  }

  const pluginId = args.id || manifest?.id || manifest?.name || path.basename(pluginPath);
  result.id = pluginId;
  result.config.status = configContainsId(result.config.path, pluginId);
  if (result.config.status === "missing-config") {
    warnings.push("User-level Codex config was not found");
  }
  if (result.config.status === "missing-id") {
    warnings.push("User-level Codex config does not contain plugin id " + pluginId);
  }

  if (args.cache) {
    const cachePath = path.resolve(args.cache);
    result.cache = { path: cachePath, status: "missing", drift: "unchecked" };
    if (!existsSync(cachePath) || !statSync(cachePath).isDirectory()) {
      warnings.push("Cache path does not exist or is not a directory");
    } else if (result.plugin.status === "present") {
      result.cache.status = "present";
      result.cache.drift = treeHash(pluginPath) === treeHash(cachePath) ? "match" : "different";
    }
  }

  result.ok = errors.length === 0;
  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printText(result);
  }

  process.exit(result.ok ? 0 : 1);
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
