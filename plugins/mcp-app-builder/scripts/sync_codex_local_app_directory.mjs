#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function isPluginAppId(value) {
  return typeof value === "string" && /^(?:plugin_)?asdk_app_[a-z0-9]+$/i.test(value);
}

function usage() {
  return [
    "Usage:",
    "  node scripts/sync_codex_local_app_directory.mjs --plugin /path/to/plugin [--cache-dir ~/.codex/cache/codex_app_directory] [--write] [--json]",
    "",
    "Upserts .app.json entries into Codex's local app-directory cache as LOCAL_PLUGIN rows.",
    "This does not fabricate app action/tool cache entries; those must come from real app links.",
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
    cacheDir: path.join(os.homedir(), ".codex", "cache", "codex_app_directory"),
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
    if (token === "--cache-dir") {
      args.cacheDir = readValue(tokens, token);
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
  if (!args.plugin) {
    throw new Error("--plugin is required");
  }
  return args;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function titleFromKey(key) {
  return key
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

function appSlug(name, id) {
  const slug = String(name || id)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || id.replace(/_/g, "-");
}

function resolveIcon(pluginPath, icon) {
  if (typeof icon !== "string" || icon.length === 0) {
    return null;
  }
  if (/^https?:\/\//.test(icon)) {
    return icon;
  }
  if (icon.startsWith("./") || icon.startsWith("../")) {
    return path.resolve(pluginPath, icon);
  }
  return icon;
}

function appRows(pluginPath) {
  const manifest = readJson(path.join(pluginPath, ".codex-plugin", "plugin.json"));
  const appManifest = readJson(path.join(pluginPath, ".app.json"));
  const apps = appManifest.apps && typeof appManifest.apps === "object" && !Array.isArray(appManifest.apps)
    ? appManifest.apps
    : {};
  const includes = Array.isArray(manifest.interface?.includes) ? manifest.interface.includes : [];
  const displayName = manifest.interface?.displayName || manifest.name || path.basename(pluginPath);
  const developer = manifest.interface?.developerName || manifest.author?.name || "Local Plugin";
  const version = manifest.version || "0.0.0";

  return Object.entries(apps).map(([key, app]) => {
    if (!app || typeof app !== "object") {
      throw new Error(".app.json apps." + key + " must be an object");
    }
    const id = app.id;
    if (!isPluginAppId(id)) {
      throw new Error(
        ".app.json apps." + key +
          ".id must start with plugin_asdk_app_ (legacy asdk_app_ is accepted)"
      );
    }
    const include = includes.find((entry) => entry && entry.kind === "app" && entry.name === key) || {};
    const name = app.name || include.title || include.displayName || include.description?.replace(/\s+app\.?$/i, "") || titleFromKey(key);
    const description = app.description || include.description || "Local app for " + displayName + ".";
    const category = app.category || "DEVELOPER_TOOLS";
    const icon = resolveIcon(pluginPath, include.icon || app.icon || manifest.interface?.logo);
    const installUrl = app.installUrl || "https://chatgpt.com/apps/" + appSlug(name, id) + "/" + id;
    return {
      id,
      name,
      description,
      installUrl,
      distributionChannel: "LOCAL_PLUGIN",
      isAccessible: true,
      isEnabled: true,
      logoUrl: icon,
      logoUrlDark: icon,
      labels: { interactive: "true" },
      pluginDisplayNames: [displayName],
      branding: null,
      appMetadata: {
        categories: [category],
        developer: { name: developer },
        firstPartyRequiresInstall: null,
        firstPartyType: null,
        review: { status: "UNSET" },
        screenshots: null,
        seoDescription: null,
        showInComposerWhenUnlinked: true,
        subCategories: null,
        version,
        versionId: null,
        versionNotes: null,
      },
    };
  });
}

function syncFile(filePath, rows, write) {
  const data = readJson(filePath);
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw new Error(filePath + " must contain a JSON object");
  }
  if (!Array.isArray(data.connectors)) {
    throw new Error(filePath + " must contain a connectors array");
  }
  const before = data.connectors.length;
  const indexes = new Map();
  data.connectors.forEach((row, index) => {
    if (row && typeof row.id === "string") {
      indexes.set(row.id, index);
    }
  });
  let updated = 0;
  let inserted = 0;
  for (const row of rows) {
    const index = indexes.get(row.id);
    if (typeof index === "number") {
      data.connectors[index] = { ...data.connectors[index], ...row };
      updated += 1;
    } else {
      data.connectors.push(row);
      indexes.set(row.id, data.connectors.length - 1);
      inserted += 1;
    }
  }
  if (write) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n");
  }
  return { filePath, before, after: data.connectors.length, updated, inserted };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const pluginPath = path.resolve(args.plugin);
  const cacheDir = path.resolve(args.cacheDir);
  const rows = appRows(pluginPath);
  if (rows.length === 0) {
    throw new Error("No apps found in " + path.join(pluginPath, ".app.json"));
  }
  const files = fs.readdirSync(cacheDir)
    .filter((name) => name.endsWith(".json"))
    .map((name) => path.join(cacheDir, name))
    .sort();
  if (files.length === 0) {
    throw new Error("No app-directory cache files found in " + cacheDir);
  }
  const result = {
    plugin: pluginPath,
    cacheDir,
    write: args.write,
    apps: rows.map((row) => ({ id: row.id, name: row.name, installUrl: row.installUrl })),
    files: files.map((filePath) => syncFile(filePath, rows, args.write)),
  };
  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  console.log((args.write ? "Synced" : "Would sync") + " " + rows.length + " local app(s)");
  for (const row of rows) {
    console.log("- " + row.name + " (" + row.id + ")");
  }
  for (const file of result.files) {
    console.log("- " + file.filePath + ": updated=" + file.updated + " inserted=" + file.inserted);
  }
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
