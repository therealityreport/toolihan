#!/usr/bin/env node

import {
  copyFileSync,
  existsSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";

const DEFAULT_EXPECTED_KEYS = ["pdfx", "iconify", "shoogle", "shadcn"];
const BANNED_RENDERER_ONLY_NAMES = [
  "render_pdfx_app",
  "render_iconify_app",
  "render_shoogle_app",
  "render_shadcn_app",
];
const TEXT_EXTENSIONS = new Set([
  ".js",
  ".mjs",
  ".cjs",
  ".ts",
  ".tsx",
  ".jsx",
  ".json",
  ".md",
  ".html",
  ".css",
  ".toml",
  ".yaml",
  ".yml",
]);

function isPluginAppId(value) {
  return typeof value === "string" && /^(?:plugin_)?asdk_app_[a-z0-9]+$/i.test(value);
}

function usage() {
  return [
    "Usage:",
    "  node scripts/check_mcp_app_state.mjs --plugin /path/to/plugin [--bridges /path/to/tunnels.json] [--expected pdfx,iconify,shoogle,shadcn] [--codex-app-tools /path/to/codex_apps_tools] [--require-codex-action-cache] [--strict-stable-urls] [--json] [--watch] [--interval 5]",
    "  node scripts/check_mcp_app_state.mjs --all-installed [--config /path/to/config.toml] [--plugin-cache-root /path/to/plugins/cache] [--codex-app-tools /path/to/codex_apps_tools] [--source-root /path/to/source] [--dry-run|--apply] [--json]",
    "  node scripts/check_mcp_app_state.mjs --rollback /path/to/file.bak-mcp-app-state-... [--json]",
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
  const args = {
    plugin: null,
    allInstalled: false,
    config: path.join(os.homedir(), ".codex", "config.toml"),
    pluginCacheRoot: path.join(os.homedir(), ".codex", "plugins", "cache"),
    sourceRoot: null,
    bridges: null,
    expected: DEFAULT_EXPECTED_KEYS,
    codexAppTools: path.join(os.homedir(), ".codex", "cache", "codex_apps_tools"),
    requireCodexActionCache: false,
    strictStableUrls: false,
    json: false,
    apply: false,
    dryRun: false,
    rollback: null,
    watch: false,
    interval: 5,
  };
  const tokens = [...argv];

  while (tokens.length > 0) {
    const token = tokens.shift();
    if (token === "--plugin") {
      args.plugin = readValue(tokens, token);
      continue;
    }
    if (token === "--all-installed") {
      args.allInstalled = true;
      continue;
    }
    if (token === "--config" || token === "--config-path") {
      args.config = readValue(tokens, token);
      continue;
    }
    if (token === "--plugin-cache-root" || token === "--plugin-cache") {
      args.pluginCacheRoot = readValue(tokens, token);
      continue;
    }
    if (token === "--source-root" || token === "--source") {
      args.sourceRoot = readValue(tokens, token);
      continue;
    }
    if (token === "--bridges") {
      args.bridges = readValue(tokens, token);
      continue;
    }
    if (token === "--expected") {
      const value = readValue(tokens, token);
      args.expected = value === "none" ? [] : value.split(",").map((item) => item.trim()).filter(Boolean);
      continue;
    }
    if (token === "--codex-app-tools" || token === "--action-cache-dir") {
      args.codexAppTools = readValue(tokens, token);
      continue;
    }
    if (token === "--require-codex-action-cache") {
      args.requireCodexActionCache = true;
      continue;
    }
    if (token === "--strict-stable-urls") {
      args.strictStableUrls = true;
      continue;
    }
    if (token === "--json") {
      args.json = true;
      continue;
    }
    if (token === "--apply") {
      args.apply = true;
      continue;
    }
    if (token === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (token === "--rollback" || token === "--rollback-backup") {
      args.rollback = readValue(tokens, token);
      continue;
    }
    if (token === "--backup") {
      args.rollback = readValue(tokens, token);
      continue;
    }
    if (token === "--watch") {
      args.watch = true;
      continue;
    }
    if (token === "--interval") {
      const value = Number(readValue(tokens, token));
      if (!Number.isFinite(value) || value <= 0) {
        throw new Error("--interval must be a positive number of seconds");
      }
      args.interval = value;
      continue;
    }
    if (token === "--help" || token === "-h") {
      console.log(usage());
      process.exit(0);
    }
    throw new Error("Unknown argument: " + token);
  }

  if (!args.plugin && !args.allInstalled && !args.rollback) {
    throw new Error("Missing required --plugin.\n\n" + usage());
  }

  if (args.allInstalled && args.plugin) {
    throw new Error("Use either --plugin or --all-installed, not both");
  }
  if (args.apply && args.dryRun) {
    throw new Error("Use either --apply or --dry-run, not both");
  }
  if ((args.apply || args.dryRun) && !args.allInstalled) {
    throw new Error("--apply and --dry-run require --all-installed");
  }
  if (args.rollback && (args.allInstalled || args.plugin)) {
    throw new Error("--rollback cannot be combined with --plugin or --all-installed");
  }

  return args;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function readJson(filePath, errors) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    errors.push(path.basename(filePath) + " is not valid JSON: " + error.message);
    return null;
  }
}

function classifyUrl(value) {
  if (!value) {
    return "missing";
  }

  let url;
  try {
    url = new URL(value);
  } catch {
    return "missing";
  }

  const host = url.hostname.toLowerCase();
  if (
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "::1" ||
    host.startsWith("10.") ||
    host.startsWith("192.168.") ||
    /^172\.(1[6-9]|2\d|3[0-1])\./.test(host)
  ) {
    return "local";
  }

  if (
    host.endsWith("trycloudflare.com") ||
    host.endsWith("loca.lt") ||
    host.endsWith("ngrok-free.app") ||
    host.endsWith("ngrok.io")
  ) {
    return "ephemeral";
  }

  if (url.protocol === "https:") {
    return "stable";
  }

  return "ephemeral";
}

function collectUrls(value, urls = []) {
  if (typeof value === "string") {
    if (/^https?:\/\//.test(value)) {
      urls.push(value);
    }
    return urls;
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      collectUrls(item, urls);
    }
    return urls;
  }
  if (value && typeof value === "object") {
    for (const item of Object.values(value)) {
      collectUrls(item, urls);
    }
  }
  return urls;
}

function syntheticLinkForAppId(appId) {
  return isPluginAppId(appId)
    ? "link_" + appId.replace(/^(?:plugin_)?asdk_app_/i, "")
    : null;
}

function collectCodexActionCache(apps, toolsDir, errors, warnings, requireCache) {
  const result = {
    path: toolsDir,
    status: "missing",
    apps: [],
  };

  if (!toolsDir) {
    result.status = "not-supplied";
    return result;
  }

  if (!existsSync(toolsDir) || !statSync(toolsDir).isDirectory()) {
    warnings.push("Codex app tools cache was not found");
    return result;
  }

  result.status = "present";
  const byId = new Map();
  for (const [key, app] of Object.entries(apps)) {
    if (!app || typeof app !== "object" || typeof app.id !== "string") {
      continue;
    }
    byId.set(app.id, {
      key,
      id: app.id,
      status: "missing",
      toolCount: 0,
      linkIds: new Set(),
      namespaces: new Set(),
      syntheticLinkIds: new Set(),
      files: new Set(),
    });
  }

  for (const file of readdirSync(toolsDir)) {
    if (!file.endsWith(".json")) {
      continue;
    }
    const filePath = path.join(toolsDir, file);
    const document = readJson(filePath, errors);
    if (!document || !Array.isArray(document.tools)) {
      continue;
    }
    for (const tool of document.tools) {
      const record = byId.get(tool?.connector_id);
      if (!record) {
        continue;
      }
      const meta = tool.tool && typeof tool.tool === "object" ? tool.tool._meta : null;
      const linkId = typeof meta?.link_id === "string" ? meta.link_id : null;
      record.toolCount += 1;
      record.files.add(file);
      if (typeof tool.tool_namespace === "string") {
        record.namespaces.add(tool.tool_namespace);
      }
      if (linkId) {
        record.linkIds.add(linkId);
        if (linkId === syntheticLinkForAppId(record.id)) {
          record.syntheticLinkIds.add(linkId);
        }
      }
    }
  }

  for (const record of byId.values()) {
    if (record.toolCount > 0) {
      record.status = record.syntheticLinkIds.size > 0 ? "synthetic" : "ok";
    }
    if (record.status === "missing" && requireCache) {
      errors.push("Missing Codex action cache for apps." + record.key + " (" + record.id + ")");
    }
    if (record.status === "synthetic") {
      errors.push("Synthetic Codex action link found for apps." + record.key + ": " + [...record.syntheticLinkIds].join(","));
    }
    result.apps.push({
      key: record.key,
      id: record.id,
      status: record.status,
      toolCount: record.toolCount,
      linkIds: [...record.linkIds].sort(),
      namespaces: [...record.namespaces].sort(),
      files: [...record.files].sort(),
    });
  }

  return result;
}

function validateMcpEntry(key, entry, errors) {
  if (!entry || typeof entry !== "object") {
    errors.push("mcpServers." + key + " must be an object");
    return { key, status: "invalid", type: "missing" };
  }
  if (typeof entry.command === "string" && entry.command.length > 0) {
    return { key, status: "ok", type: "command" };
  }
  if (typeof entry.url === "string" && entry.url.length > 0) {
    return { key, status: "ok", type: "url", url: entry.url, stability: classifyUrl(entry.url) };
  }
  errors.push("mcpServers." + key + " must define command or url");
  return { key, status: "invalid", type: "missing" };
}

function collectTextFiles(root, relativeDir = "") {
  const dir = path.join(root, relativeDir);
  if (!existsSync(dir)) {
    return [];
  }

  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules" || entry.name === "dist") {
      continue;
    }
    const relativePath = path.join(relativeDir, entry.name);
    const fullPath = path.join(root, relativePath);
    if (entry.isDirectory()) {
      files.push(...collectTextFiles(root, relativePath));
      continue;
    }
    if (entry.isFile() && TEXT_EXTENSIONS.has(path.extname(entry.name))) {
      files.push(fullPath);
    }
  }
  return files;
}

function actionSurfaceRoots(root) {
  const candidates = [
    "apps/personal-mcp-apps/src",
    "src",
    "server",
    "apps",
  ]
    .map((relativePath) => path.join(root, relativePath))
    .filter((candidate) => existsSync(candidate) && statSync(candidate).isDirectory());
  return candidates.length > 0 ? candidates : [root];
}

function scanBannedNames(root) {
  const matches = [];
  for (const surfaceRoot of actionSurfaceRoots(root)) {
    for (const filePath of collectTextFiles(surfaceRoot)) {
      const text = readFileSync(filePath, "utf8");
      for (const name of BANNED_RENDERER_ONLY_NAMES) {
        if (text.includes(name)) {
          matches.push({ file: path.relative(root, filePath), name });
        }
      }
    }
  }
  return matches;
}

function printText(result) {
  console.log("MCP app state check");
  console.log("- plugin: " + result.plugin.status + " (" + result.plugin.path + ")");
  console.log("- .app.json: " + result.app.status);
  console.log("- .mcp.json: " + result.mcp.status);
  for (const app of result.apps) {
    console.log("- app " + app.key + ": " + app.status + " (" + (app.id || "missing id") + ")");
  }
  for (const server of result.mcpServers) {
    const detail = server.type === "url" ? server.type + ", " + server.stability : server.type;
    console.log("- mcp " + server.key + ": " + server.status + " (" + detail + ")");
  }
  for (const bridge of result.bridges.urls) {
    console.log("- bridge url: " + bridge.stability + " (" + bridge.url + ")");
  }
  console.log("- codex action cache: " + result.codexActionCache.status + " (" + result.codexActionCache.path + ")");
  for (const app of result.codexActionCache.apps) {
    console.log("- codex action " + app.key + ": " + app.status + " (" + app.toolCount + " tools, links: " + (app.linkIds.join(",") || "none") + ")");
  }
  console.log("- banned renderer-only names: " + result.banned.status);
  for (const warning of result.warnings) {
    console.log("- warning: " + warning);
  }
  for (const error of result.errors) {
    console.log("- error: " + error);
  }
}

function printCompactText(result) {
  const warnings = result.warnings.length;
  const errors = result.errors.length;
  const apps = result.apps.map((app) => app.key + ":" + app.status).join(",");
  const mcpServers = result.mcpServers.map((server) => server.key + ":" + server.status).join(",");
  const codexActionCache = result.codexActionCache.apps.map((app) => app.key + ":" + app.status).join(",");
  console.log([
    new Date().toISOString(),
    result.ok ? "ok" : "error",
    "apps=" + (apps || "none"),
    "mcp=" + (mcpServers || "none"),
    "codex_actions=" + (codexActionCache || "none"),
    "warnings=" + warnings,
    "errors=" + errors,
  ].join(" "));
  for (const warning of result.warnings) {
    console.log("warning: " + warning);
  }
  for (const error of result.errors) {
    console.log("error: " + error);
  }
}

function runCheck(args) {
  const pluginPath = path.resolve(args.plugin);
  const errors = [];
  const warnings = [];
  const result = {
    ok: false,
    plugin: { path: pluginPath, status: "missing" },
    app: { path: path.join(pluginPath, ".app.json"), status: "missing" },
    mcp: { path: path.join(pluginPath, ".mcp.json"), status: "missing" },
    expected: args.expected,
    apps: [],
    mcpServers: [],
    bridges: { path: args.bridges ? path.resolve(args.bridges) : null, status: "not-supplied", urls: [] },
    codexActionCache: { path: args.codexAppTools ? path.resolve(args.codexAppTools) : null, status: "unchecked", apps: [] },
    banned: { names: BANNED_RENDERER_ONLY_NAMES, status: "unchecked", matches: [] },
    warnings,
    errors,
  };

  if (!existsSync(pluginPath) || !statSync(pluginPath).isDirectory()) {
    errors.push("Plugin path does not exist or is not a directory");
  } else {
    result.plugin.status = "present";
  }

  const appJson = existsSync(result.app.path) ? readJson(result.app.path, errors) : null;
  if (appJson) {
    result.app.status = "present";
  } else {
    errors.push("Missing root .app.json");
  }

  const mcpJson = existsSync(result.mcp.path) ? readJson(result.mcp.path, errors) : null;
  if (mcpJson) {
    result.mcp.status = "present";
  } else {
    errors.push("Missing root .mcp.json");
  }

  const apps = appJson?.apps && typeof appJson.apps === "object" ? appJson.apps : {};
  const mcpServers = mcpJson?.mcpServers && typeof mcpJson.mcpServers === "object" ? mcpJson.mcpServers : {};
  if (appJson && Object.keys(apps).length === 0) {
    errors.push(".app.json must define apps.<key>");
  }
  if (mcpJson && Object.keys(mcpServers).length === 0) {
    errors.push(".mcp.json must define mcpServers.<key>");
  }

  for (const key of args.expected) {
    if (!apps[key]) {
      errors.push("Missing apps." + key);
    }
    if (!mcpServers[key]) {
      errors.push("Missing mcpServers." + key);
    }
  }

  for (const [key, app] of Object.entries(apps)) {
    const id = app && typeof app === "object" ? app.id : null;
    const status = isPluginAppId(id) ? "ok" : "invalid";
    if (status !== "ok") {
      errors.push(
        "apps." + key + ".id must start with plugin_asdk_app_ (legacy asdk_app_ is accepted)"
      );
    }
    result.apps.push({ key, id, status });
  }

  for (const [key, entry] of Object.entries(mcpServers)) {
    const server = validateMcpEntry(key, entry, errors);
    if (server.stability === "ephemeral") {
      warnings.push("mcpServers." + key + " uses an ephemeral URL");
    }
    result.mcpServers.push(server);
  }

  result.codexActionCache = collectCodexActionCache(
    apps,
    args.codexAppTools ? path.resolve(args.codexAppTools) : null,
    errors,
    warnings,
    args.requireCodexActionCache
  );

  if (args.bridges) {
    const bridgePath = path.resolve(args.bridges);
    result.bridges.path = bridgePath;
    if (!existsSync(bridgePath) || !statSync(bridgePath).isFile()) {
      warnings.push("Bridge metadata file was not found");
      result.bridges.status = "missing";
    } else {
      const bridges = readJson(bridgePath, errors);
      result.bridges.status = bridges ? "present" : "invalid";
      for (const url of collectUrls(bridges)) {
        const stability = classifyUrl(url);
        if (stability === "ephemeral") {
          warnings.push("Bridge URL is ephemeral: " + url);
        }
        result.bridges.urls.push({ url, stability });
      }
    }
  }

  result.banned.matches = result.plugin.status === "present" ? scanBannedNames(pluginPath) : [];
  result.banned.status = result.banned.matches.length === 0 ? "absent" : "present";
  for (const match of result.banned.matches) {
    errors.push("Banned renderer-only name " + match.name + " found in " + match.file);
  }

  if (args.strictStableUrls) {
    for (const server of result.mcpServers) {
      if (server.stability === "ephemeral") {
        errors.push("Strict URL stability failed for mcpServers." + server.key);
      }
    }
    for (const bridge of result.bridges.urls) {
      if (bridge.stability === "ephemeral") {
        errors.push("Strict URL stability failed for bridge URL " + bridge.url);
      }
    }
  }

  result.ok = errors.length === 0;
  return result;
}

function printResult(result, args) {
  if (args.json) {
    console.log(JSON.stringify(result, null, args.watch ? 0 : 2));
  } else if (args.watch) {
    printCompactText(result);
  } else {
    printText(result);
  }
}

/*
 * The all-installed doctor deliberately uses a tiny TOML reader rather than a
 * dependency.  It only reads the two tables that are relevant to this
 * inventory (`apps.*` and `plugins.*`) and ignores the rest of config.toml.
 */
function stripTomlComment(line) {
  let quoted = false;
  let escaped = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === "\\" && quoted && !escaped) {
      escaped = true;
      continue;
    }
    if (char === '"' && !escaped) {
      quoted = !quoted;
    }
    if (char === "#" && !quoted) {
      return line.slice(0, index);
    }
    escaped = false;
  }
  return line;
}

function parseTomlKey(value) {
  const trimmed = value.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    try {
      return JSON.parse(trimmed);
    } catch {
      return trimmed.slice(1, -1);
    }
  }
  return trimmed;
}

function parseTomlScalar(value) {
  const trimmed = value.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    try {
      return JSON.parse(trimmed);
    } catch {
      return trimmed.slice(1, -1);
    }
  }
  return trimmed;
}

function parseInstalledConfig(configPath, errors) {
  const result = {
    path: configPath,
    status: "missing",
    apps: new Map(),
    plugins: new Map(),
  };
  if (!existsSync(configPath) || !statSync(configPath).isFile()) {
    errors.push("Config file was not found");
    return result;
  }

  let text;
  try {
    text = readFileSync(configPath, "utf8");
  } catch (error) {
    errors.push("Config file could not be read: " + error.message);
    return result;
  }

  let section = null;
  for (const rawLine of text.split(/\r?\n/)) {
    const line = stripTomlComment(rawLine).trim();
    if (!line) continue;
    const sectionMatch = line.match(/^\[([^\]]+)\]$/);
    if (sectionMatch) {
      const value = sectionMatch[1];
      const appMatch = value.match(/^apps\.(?:"((?:\\.|[^"])*)"|(.+))$/);
      const pluginMatch = value.match(/^plugins\.(?:"((?:\\.|[^"])*)"|(.+))$/);
      if (appMatch) {
        section = { type: "app", key: parseTomlKey(appMatch[1] || appMatch[2]) };
      } else if (pluginMatch) {
        section = { type: "plugin", key: parseTomlKey(pluginMatch[1] || pluginMatch[2]) };
      } else {
        section = null;
      }
      continue;
    }

    const assignment = line.match(/^([A-Za-z0-9_.-]+)\s*=\s*(.+)$/);
    if (!assignment || !section) continue;
    const key = assignment[1];
    const value = parseTomlScalar(assignment[2]);
    if (key !== "enabled" || typeof value !== "boolean") continue;
    const target = section.type === "app" ? result.apps : result.plugins;
    if (section.key !== "_default") {
      target.set(section.key, { id: section.key, enabled: value });
    }
  }
  result.status = "present";
  return result;
}

function walkFiles(root, predicate, output = []) {
  if (!existsSync(root) || !statSync(root).isDirectory()) return output;
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules" || entry.name === "dist") {
      continue;
    }
    const fullPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      walkFiles(fullPath, predicate, output);
    } else if (entry.isFile() && predicate(entry.name, fullPath)) {
      output.push(fullPath);
    }
  }
  return output;
}

function cachePathParts(cacheRoot, manifestPath) {
  const relative = path.relative(cacheRoot, manifestPath).split(path.sep);
  const fileIndex = relative.lastIndexOf(".app.json");
  const beforeFile = fileIndex >= 0 ? relative.slice(0, fileIndex) : relative.slice(0, -1);
  return {
    source: beforeFile.length >= 3 ? beforeFile[0] : null,
    plugin: beforeFile.length >= 3 ? beforeFile[beforeFile.length - 2] : null,
    version: beforeFile.length >= 3 ? beforeFile[beforeFile.length - 1] : null,
  };
}

function statusHint(value) {
  if (typeof value !== "string") return null;
  const normalized = value.toLowerCase().replace(/[ -]/g, "_");
  if (normalized.includes("auth") || normalized.includes("sign_in") || normalized.includes("permission")) {
    return "auth_required";
  }
  if (normalized.includes("connection") || normalized.includes("transport") || normalized.includes("failed")) {
    return "connection_failed";
  }
  return null;
}

function readManifestStatus(document) {
  if (!document || typeof document !== "object") return null;
  const candidates = [document.status, document.state, document.error_class, document.errorClass];
  for (const candidate of candidates) {
    const hint = statusHint(candidate);
    if (hint) return hint;
  }
  if (document.auth_required === true || document.authRequired === true) return "auth_required";
  if (document.connection_failed === true || document.connectionFailed === true) return "connection_failed";
  return null;
}

function collectInstalledManifests(cacheRoot, errors) {
  const manifests = [];
  const files = walkFiles(cacheRoot, (name) => name === ".app.json");
  for (const filePath of files.sort()) {
    const document = readJson(filePath, errors);
    if (!document || !document.apps || typeof document.apps !== "object") {
      errors.push(path.relative(cacheRoot, filePath) + " must define apps");
      continue;
    }
    const parts = cachePathParts(cacheRoot, filePath);
    const mcpPath = path.join(path.dirname(filePath), ".mcp.json");
    for (const [key, app] of Object.entries(document.apps)) {
      if (!app || typeof app !== "object" || typeof app.id !== "string") {
        errors.push(path.relative(cacheRoot, filePath) + ".apps." + key + ".id is missing");
        continue;
      }
      manifests.push({
        id: app.id,
        key,
        manifestPath: filePath,
        pluginRoot: path.dirname(filePath),
        source: parts.source,
        plugin: parts.plugin,
        version: parts.version,
        hasMcp: existsSync(mcpPath),
        mcpPath: existsSync(mcpPath) ? mcpPath : null,
        statusHint: readManifestStatus(app) || readManifestStatus(document),
      });
    }
  }
  return manifests;
}

function canonicalJson(value) {
  if (Array.isArray(value)) return value.map(canonicalJson);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalJson(value[key])]));
  }
  return value;
}

function jsonDocumentsEqual(firstPath, secondPath, errors) {
  const first = readJson(firstPath, errors);
  const second = readJson(secondPath, errors);
  if (first === null || second === null) return false;
  return JSON.stringify(canonicalJson(first)) === JSON.stringify(canonicalJson(second));
}

function collectSourceManifests(sourceRoot, errors) {
  if (!sourceRoot) return new Map();
  const result = new Map();
  const files = walkFiles(path.resolve(sourceRoot), (name) => name === ".app.json");
  for (const filePath of files.sort()) {
    const document = readJson(filePath, errors);
    if (!document || !document.apps || typeof document.apps !== "object") continue;
    for (const [key, app] of Object.entries(document.apps)) {
      if (!app || typeof app.id !== "string") continue;
      const rows = result.get(app.id) || [];
      rows.push({
        id: app.id,
        key,
        manifestPath: filePath,
        pluginRoot: path.dirname(filePath),
        plugin: path.basename(path.dirname(filePath)),
      });
      result.set(app.id, rows);
    }
  }
  return result;
}

function collectAllActionCache(cacheRoot, errors) {
  const result = {
    path: cacheRoot,
    status: "missing",
    files: [],
    byId: new Map(),
    malformedFiles: [],
  };
  if (!cacheRoot || !existsSync(cacheRoot) || !statSync(cacheRoot).isDirectory()) return result;
  result.status = "present";
  const files = readdirSync(cacheRoot).filter((file) => file.endsWith(".json")).sort();
  for (const file of files) {
    const filePath = path.join(cacheRoot, file);
    let document;
    try {
      document = JSON.parse(readFileSync(filePath, "utf8"));
    } catch (error) {
      result.malformedFiles.push(file);
      errors.push(file + " is not valid JSON: " + error.message);
      continue;
    }
    if (!document || !Array.isArray(document.tools)) continue;
    const fileRecord = { file, path: filePath, document, changed: false, removed: 0 };
    result.files.push(fileRecord);
    for (const tool of document.tools) {
      const id = typeof tool?.connector_id === "string"
        ? tool.connector_id
        : typeof tool?.tool?._meta?.connector_id === "string"
          ? tool.tool._meta.connector_id
          : null;
      if (!id) continue;
      const record = result.byId.get(id) || {
        id,
        toolCount: 0,
        files: new Set(),
        linkIds: new Set(),
        toolNames: new Set(),
        links: new Map(),
        statusHints: new Set(),
      };
      const documentHint = readManifestStatus(document);
      if (documentHint) record.statusHints.add(documentHint);
      const meta = tool.tool && typeof tool.tool === "object" ? tool.tool._meta : null;
      const linkId = typeof meta?.link_id === "string" ? meta.link_id : null;
      const toolName = typeof tool.tool_name === "string"
        ? tool.tool_name
        : typeof tool.tool?.name === "string" ? tool.tool.name : null;
      record.toolCount += 1;
      record.files.add(file);
      if (linkId) {
        record.linkIds.add(linkId);
        const linkTools = record.links.get(linkId) || new Set();
        if (toolName) linkTools.add(toolName);
        record.links.set(linkId, linkTools);
      }
      if (toolName) record.toolNames.add(toolName);
      for (const candidate of [tool.status, tool.state, tool.error_class, tool.errorClass]) {
        const hint = statusHint(candidate);
        if (hint) record.statusHints.add(hint);
      }
      if (tool.auth_required === true || tool.authRequired === true) record.statusHints.add("auth_required");
      if (tool.connection_failed === true || tool.connectionFailed === true) record.statusHints.add("connection_failed");
      result.byId.set(id, record);
    }
  }
  return result;
}

function installedOwnership(manifests) {
  if (manifests.some((item) => item.hasMcp)) return "bundled_mcp_app";
  if (manifests.some((item) => item.id.startsWith("connector_")) || manifests.length > 1) {
    return "shared_connector";
  }
  return "hosted_app";
}

function linkOverlap(record) {
  const links = [...record.links.entries()].sort(([a], [b]) => a.localeCompare(b));
  const overlap = [];
  for (let index = 0; index < links.length; index += 1) {
    for (let other = index + 1; other < links.length; other += 1) {
      const common = [...links[index][1]].filter((name) => links[other][1].has(name)).sort();
      if (common.length > 0) {
        overlap.push({ links: [links[index][0], links[other][0]], toolNames: common });
      }
    }
  }
  return overlap;
}

function sourceDriftFor(manifests, sourceManifests, errors) {
  if (!sourceManifests || sourceManifests.size === 0) return [];
  const drift = [];
  for (const installed of manifests) {
    if (!installed.plugin) continue;
    const candidates = (sourceManifests.get(installed.id) || []).filter((source) =>
      source.plugin === installed.plugin
    );
    for (const source of candidates) {
      const manifestEqual = jsonDocumentsEqual(installed.manifestPath, source.manifestPath, errors);
      const installedMcp = installed.mcpPath;
      const sourceMcp = path.join(source.pluginRoot, ".mcp.json");
      const mcpEqual = installedMcp && existsSync(sourceMcp)
        ? jsonDocumentsEqual(installedMcp, sourceMcp, errors)
        : installedMcp === null && !existsSync(sourceMcp);
      if (!manifestEqual || !mcpEqual) {
        drift.push({ id: installed.id, cachePath: installed.pluginRoot, sourcePath: source.pluginRoot });
      }
    }
  }
  return drift;
}

function buildAllInstalledResult(args) {
  const errors = [];
  const warnings = [];
  const config = parseInstalledConfig(path.resolve(args.config), errors);
  const manifests = collectInstalledManifests(path.resolve(args.pluginCacheRoot), errors);
  const sourceManifests = collectSourceManifests(args.sourceRoot, errors);
  const actionCache = collectAllActionCache(path.resolve(args.codexAppTools), errors);
  const manifestsById = new Map();
  for (const manifest of manifests) {
    const rows = manifestsById.get(manifest.id) || [];
    rows.push(manifest);
    manifestsById.set(manifest.id, rows);
  }
  const drift = new Set(sourceDriftFor(manifests, sourceManifests, errors).map((item) => item.id));
  const ids = new Set([...config.apps.keys(), ...manifestsById.keys()]);
  const apps = [];
  for (const id of [...ids].sort()) {
    const configRow = config.apps.get(id) || null;
    const installed = manifestsById.get(id) || [];
    const action = actionCache.byId.get(id) || null;
    const statusHints = new Set(installed.map((item) => item.statusHint).filter(Boolean));
    if (action) for (const hint of action.statusHints) statusHints.add(hint);
    let status;
    let ownership = installed.length > 0 ? installedOwnership(installed) : null;
    if (configRow && configRow.enabled === false && action) {
      status = "disabled_but_cached";
    } else if (configRow && installed.length === 0) {
      status = "orphan_config";
    } else if (drift.has(id)) {
      status = "source_cache_drift";
    } else if (statusHints.has("auth_required")) {
      status = "auth_required";
    } else if (statusHints.has("connection_failed")) {
      status = "connection_failed";
    } else if (configRow && configRow.enabled === true && !action && ownership !== "shared_connector") {
      status = "enabled_not_loaded";
    } else {
      status = ownership || "orphan_config";
    }
    const actionInfo = action
      ? {
          toolCount: action.toolCount,
          files: [...action.files].sort(),
          linkIds: [...action.linkIds].sort(),
          toolNames: [...action.toolNames].sort(),
          linkToolOverlap: linkOverlap(action),
        }
      : { toolCount: 0, files: [], linkIds: [], toolNames: [], linkToolOverlap: [] };
    apps.push({
      id,
      enabled: configRow ? configRow.enabled : null,
      ownership,
      status,
      classification: status,
      plugins: installed
        .map((item) => ({
          source: item.source,
          plugin: item.plugin,
          version: item.version,
          hasMcp: item.hasMcp,
        }))
        .sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b))),
      actionCache: actionInfo,
    });
  }

  const blocking = apps.filter((app) =>
    ["disabled_but_cached", "source_cache_drift", "connection_failed"].includes(app.status)
  );
  const orphanActionIds = [...actionCache.byId.keys()]
    .filter((id) => !ids.has(id))
    .sort();
  if (orphanActionIds.length > 0) {
    warnings.push("Action cache contains unmapped connector IDs; no automatic removal is permitted");
  }
  return {
    mode: "all-installed",
    ok: errors.length === 0 && blocking.length === 0,
    config: { path: config.path, status: config.status },
    pluginCache: { path: path.resolve(args.pluginCacheRoot), manifestCount: manifests.length },
    sourceRoot: args.sourceRoot ? path.resolve(args.sourceRoot) : null,
    actionCache: {
      path: actionCache.path,
      status: actionCache.status,
      files: actionCache.files.map((item) => item.file).sort(),
      malformedFiles: [...actionCache.malformedFiles].sort(),
      unmappedConnectorIds: orphanActionIds,
    },
    apps,
    repairs: {
      mode: args.apply ? "apply" : args.dryRun ? "dry-run" : "check",
      disabledCachedIds: apps.filter((app) => app.status === "disabled_but_cached").map((app) => app.id),
      changedFiles: [],
      backups: [],
      changedTools: 0,
    },
    warnings,
    errors,
    _actionCache: actionCache,
  };
}

function backupPathFor(filePath) {
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  let candidate = filePath + ".bak-mcp-app-state-" + stamp;
  let suffix = 1;
  while (existsSync(candidate)) {
    candidate = filePath + ".bak-mcp-app-state-" + stamp + "-" + suffix;
    suffix += 1;
  }
  return candidate;
}

function applyAllInstalledRepair(result) {
  const disabledIds = new Set(result.repairs.disabledCachedIds);
  if (disabledIds.size === 0) return result;
  for (const fileRecord of result._actionCache.files) {
    const nextTools = fileRecord.document.tools.filter((tool) => !disabledIds.has(tool?.connector_id));
    const removed = fileRecord.document.tools.length - nextTools.length;
    if (removed === 0) continue;
    const backup = backupPathFor(fileRecord.path);
    try {
      copyFileSync(fileRecord.path, backup);
      writeFileSync(fileRecord.path, JSON.stringify({ ...fileRecord.document, tools: nextTools }, null, 2) + "\n");
      fileRecord.changed = true;
      fileRecord.removed = removed;
      result.repairs.backups.push(backup);
      result.repairs.changedFiles.push(fileRecord.file);
      result.repairs.changedTools += removed;
    } catch (error) {
      result.errors.push("Could not repair " + fileRecord.file + ": " + error.message);
    }
  }
  return result;
}

function rollbackBackup(backupPath) {
  const marker = ".bak-mcp-app-state-";
  const markerIndex = backupPath.lastIndexOf(marker);
  if (markerIndex < 0) throw new Error("Backup path must contain " + marker);
  if (!existsSync(backupPath) || !statSync(backupPath).isFile()) throw new Error("Backup file was not found");
  const target = backupPath.slice(0, markerIndex);
  copyFileSync(backupPath, target);
  return {
    mode: "rollback",
    ok: true,
    rollback: { backup: path.resolve(backupPath), target: path.resolve(target), restored: true },
    warnings: [],
    errors: [],
  };
}

function printInstalledText(result) {
  console.log("Installed MCP App state");
  console.log("- config: " + result.config.status + " (" + result.config.path + ")");
  console.log("- action cache: " + result.actionCache.status + " (" + result.actionCache.path + ")");
  for (const app of result.apps) {
    const links = app.actionCache.linkIds.join(",") || "none";
    console.log("- " + app.id + ": " + app.status + " (" + (app.ownership || "no owner") + ", links: " + links + ")");
  }
  console.log("- repair mode: " + result.repairs.mode + ", changed tools: " + result.repairs.changedTools);
  for (const warning of result.warnings) console.log("- warning: " + warning);
  for (const error of result.errors) console.log("- error: " + error);
}

function printInstalledResult(result, args) {
  const output = { ...result };
  delete output._actionCache;
  if (args.json) console.log(JSON.stringify(output, null, 2));
  else printInstalledText(output);
}

function runAllInstalled(args) {
  let result = buildAllInstalledResult(args);
  if (args.dryRun) {
    result.repairs.wouldChange = result.repairs.disabledCachedIds.length > 0;
  } else if (args.apply) {
    result = applyAllInstalledRepair(result);
    const backups = [...result.repairs.backups];
    const changedFiles = [...result.repairs.changedFiles];
    const changedTools = result.repairs.changedTools;
    const after = buildAllInstalledResult({ ...args, apply: false, dryRun: false });
    after.repairs = {
      ...after.repairs,
      mode: "apply",
      backups,
      changedFiles,
      changedTools,
      disabledCachedIds: after.apps.filter((app) => app.status === "disabled_but_cached").map((app) => app.id),
    };
    after.errors.push(...result.errors.filter((error) => !after.errors.includes(error)));
    result = after;
  }
  delete result._actionCache;
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.rollback) {
    const result = rollbackBackup(path.resolve(args.rollback));
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else console.log("Restored " + result.rollback.target + " from " + result.rollback.backup);
    process.exit(0);
  }

  if (args.allInstalled) {
    const result = runAllInstalled(args);
    printInstalledResult(result, args);
    process.exit(result.ok ? 0 : 1);
  }

  if (!args.watch) {
    const result = runCheck(args);
    printResult(result, args);
    process.exit(result.ok ? 0 : 1);
  }

  while (true) {
    const result = runCheck(args);
    printResult(result, args);
    if (!result.ok) {
      process.exit(1);
    }
    await sleep(args.interval * 1000);
  }
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
