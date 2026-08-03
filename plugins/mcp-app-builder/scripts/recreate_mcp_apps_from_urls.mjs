#!/usr/bin/env node

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const EPHEMERAL_HOSTS = [
  "trycloudflare.com",
  "loca.lt",
  "ngrok-free.app",
  "ngrok.io",
];

function usage() {
  return [
    "Usage:",
    "  node scripts/recreate_mcp_apps_from_urls.mjs [--plugin /path/to/plugin] [--bridges /path/to/tunnels.json] [--created-apps /path/to/created-apps.json] [--write] [--json]",
    "",
    "Without --write, prints a manual creation checklist.",
    "With --write, updates root .app.json from created-apps.json plugin_asdk_app_... ids.",
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
    plugin: process.cwd(),
    bridges: null,
    createdApps: null,
    write: false,
    json: false,
  };
  const tokens = [...argv];

  while (tokens.length > 0) {
    const token = tokens.shift();
    if (token === "--plugin") {
      args.plugin = readValue(tokens, token);
      continue;
    }
    if (token === "--bridges") {
      args.bridges = readValue(tokens, token);
      continue;
    }
    if (token === "--created-apps") {
      args.createdApps = readValue(tokens, token);
      continue;
    }
    if (token === "--write") {
      args.write = true;
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

  if (args.write && !args.createdApps) {
    throw new Error("--write requires --created-apps /path/to/created-apps.json");
  }

  return args;
}

function readJson(filePath) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(filePath + " is not valid JSON: " + error.message);
  }
}

function titleFromKey(key) {
  return key
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

function isUrl(value) {
  return typeof value === "string" && /^https?:\/\//.test(value);
}

function isEphemeralUrl(value) {
  if (!isUrl(value)) {
    return false;
  }
  try {
    const host = new URL(value).hostname.toLowerCase();
    return EPHEMERAL_HOSTS.some((suffix) => host === suffix || host.endsWith("." + suffix));
  } catch {
    return false;
  }
}

function normalizeBridgeMap(value) {
  const map = new Map();
  if (!value || typeof value !== "object") {
    return map;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      if (!item || typeof item !== "object") {
        continue;
      }
      const key = item.key || item.name || item.id || item.server || item.mcpServer;
      if (typeof key === "string" && key.length > 0) {
        map.set(key, item);
      }
    }
    return map;
  }

  const containers = [value.bridges, value.tunnels, value.mcpServers, value.servers];
  for (const container of containers) {
    if (container && typeof container === "object") {
      for (const [key, item] of Object.entries(container)) {
        map.set(key, item && typeof item === "object" ? item : { url: item });
      }
    }
  }

  for (const [key, item] of Object.entries(value)) {
    if (containers.includes(item)) {
      continue;
    }
    if (item && typeof item === "object") {
      map.set(key, item);
    }
  }

  return map;
}

function normalizeCreatedApps(value) {
  const map = new Map();
  if (!value || typeof value !== "object") {
    return map;
  }

  const entries = Array.isArray(value)
    ? value.map((item) => [item?.key || item?.name || item?.slug, item])
    : Object.entries(value.apps && typeof value.apps === "object" ? value.apps : value);

  for (const [key, item] of entries) {
    if (typeof key === "string" && key.length > 0 && item && typeof item === "object") {
      map.set(key, item);
    }
  }

  return map;
}

function createdAppId(entry) {
  if (!entry || typeof entry !== "object") {
    return null;
  }
  for (const field of ["id", "appId", "app_id"]) {
    if (typeof entry[field] === "string") {
      return entry[field];
    }
  }
  return null;
}

function isPluginAppId(value) {
  return typeof value === "string" && /^(?:plugin_)?asdk_app_[a-z0-9]+$/i.test(value);
}

function selectedSource(entry, bridge) {
  const entryUrl = isUrl(entry?.url) ? { kind: ".mcp.json url", value: entry.url } : null;
  if (entryUrl && !isEphemeralUrl(entryUrl.value)) {
    return entryUrl;
  }
  if (bridge && typeof bridge === "object") {
    if (isUrl(bridge.mcpUrl)) {
      return { kind: "bridge.mcpUrl", value: bridge.mcpUrl };
    }
    if (isUrl(bridge.url)) {
      return { kind: "bridge.url", value: bridge.url };
    }
  }
  if (isUrl(entry?.url)) {
    return entryUrl;
  }
  if (typeof entry?.command === "string" && entry.command.length > 0) {
    const args = Array.isArray(entry.args) ? " " + entry.args.join(" ") : "";
    return { kind: ".mcp.json command", value: entry.command + args };
  }
  return { kind: "missing", value: null };
}

function checklistFromMcp(mcpJson, bridges) {
  const servers = mcpJson?.mcpServers && typeof mcpJson.mcpServers === "object" ? mcpJson.mcpServers : {};
  const items = [];
  const warnings = [];

  for (const [key, entry] of Object.entries(servers)) {
    const bridge = bridges.get(key);
    const source = selectedSource(entry, bridge);
    const title = entry?.title || entry?.name || titleFromKey(key);
    const description = entry?.description || "MCP app for " + title + ".";
    const item = {
      key,
      title,
      description,
      selectedUrl: source.value,
      selectedSource: source.kind,
      authMode: "none",
      expectedActionSource: {
        key,
        source: source.kind,
        value: source.value,
      },
    };
    if (isEphemeralUrl(source.value)) {
      warnings.push(key + " uses an ephemeral URL: " + source.value);
      item.warning = "ephemeral-url";
    }
    items.push(item);
  }

  return { items, warnings };
}

function printChecklist(result) {
  console.log("MCP app recreation checklist");
  for (const item of result.items) {
    console.log("- " + item.key);
    console.log("  title: " + item.title);
    console.log("  description: " + item.description);
    console.log("  selected URL: " + (item.selectedUrl || "missing"));
    console.log("  auth mode: " + item.authMode);
    console.log("  expected action source: " + item.expectedActionSource.source);
    if (item.warning) {
      console.log("  warning: " + item.warning);
    }
  }
  for (const warning of result.warnings) {
    console.log("warning: " + warning);
  }
}

function writeAppJson(pluginPath, checklist, createdApps) {
  const appPath = path.join(pluginPath, ".app.json");
  if (!existsSync(appPath)) {
    throw new Error("Missing root .app.json: " + appPath);
  }

  const appJson = readJson(appPath);
  if (!appJson.apps || typeof appJson.apps !== "object" || Array.isArray(appJson.apps)) {
    appJson.apps = {};
  }

  const errors = [];
  const updated = [];
  for (const item of checklist.items) {
    const created = createdApps.get(item.key);
    if (!created) {
      continue;
    }
    const id = createdAppId(created);
    if (!isPluginAppId(id)) {
      errors.push(
        "created-apps entry for " + item.key +
          " must contain a plugin_asdk_app_... id (legacy asdk_app_... is accepted)"
      );
      continue;
    }
    const existing = appJson.apps[item.key] && typeof appJson.apps[item.key] === "object" ? appJson.apps[item.key] : {};
    appJson.apps[item.key] = {
      ...existing,
      id,
      metadata: {
        ...(existing.metadata && typeof existing.metadata === "object" ? existing.metadata : {}),
        expectedActionSource: item.expectedActionSource,
      },
    };
    updated.push({ key: item.key, id });
  }

  if (errors.length > 0) {
    throw new Error(errors.join("\n"));
  }
  if (updated.length === 0) {
    throw new Error(
      "No created-apps entries with real plugin_asdk_app_... ids matched .mcp.json servers"
    );
  }

  writeFileSync(appPath, JSON.stringify(appJson, null, 2) + "\n");
  return { appPath, updated };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const pluginPath = path.resolve(args.plugin);
  const mcpPath = path.join(pluginPath, ".mcp.json");
  if (!existsSync(mcpPath)) {
    throw new Error("Missing root .mcp.json: " + mcpPath);
  }

  const mcpJson = readJson(mcpPath);
  const bridgeJson = args.bridges ? readJson(path.resolve(args.bridges)) : null;
  const bridges = normalizeBridgeMap(bridgeJson);
  const result = {
    plugin: pluginPath,
    mcpPath,
    bridgePath: args.bridges ? path.resolve(args.bridges) : null,
    ...checklistFromMcp(mcpJson, bridges),
  };

  if (args.write) {
    const createdJson = readJson(path.resolve(args.createdApps));
    const writeResult = writeAppJson(pluginPath, result, normalizeCreatedApps(createdJson));
    const output = { ...result, write: writeResult };
    if (args.json) {
      console.log(JSON.stringify(output, null, 2));
    } else {
      console.log("Updated " + writeResult.appPath);
      for (const app of writeResult.updated) {
        console.log("- " + app.key + ": " + app.id);
      }
      for (const warning of result.warnings) {
        console.log("warning: " + warning);
      }
    }
    return;
  }

  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printChecklist(result);
  }
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
