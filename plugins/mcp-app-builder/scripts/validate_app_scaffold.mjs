#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

const SECRET_PATTERNS = [
  "[TODO" + ":",
  "OPENAI" + "_API_KEY=",
  "sk" + "-",
  "your" + "_api_key",
  "YOUR" + "_API_KEY",
  "api" + "Key:",
  "api" + "_key:",
];

function usage() {
  return "Usage: node scripts/validate_app_scaffold.mjs <app-directory>";
}

function readText(filePath) {
  return readFileSync(filePath, "utf8");
}

function readJson(filePath, errors) {
  try {
    return JSON.parse(readText(filePath));
  } catch (error) {
    errors.push(path.basename(filePath) + " is not valid JSON: " + error.message);
    return null;
  }
}

function isPluginAppId(value) {
  return typeof value === "string" && /^(?:plugin_)?asdk_app_[a-z0-9]+$/i.test(value);
}

function requireFile(root, relativePath, errors) {
  const filePath = path.join(root, relativePath);
  if (!existsSync(filePath) || !statSync(filePath).isFile()) {
    errors.push("Missing " + relativePath);
    return null;
  }
  return filePath;
}

function requireString(contents, needle, label, errors) {
  if (!contents.includes(needle)) {
    errors.push(label + " must include `" + needle + "`");
  }
}

function countMatches(contents, pattern) {
  return Array.from(contents.matchAll(pattern)).length;
}

function requirePatternCount(contents, pattern, minimum, message, errors) {
  const count = countMatches(contents, pattern);
  if (count < minimum) {
    errors.push(message + " (" + count + "/" + minimum + ")");
  }
}

function validateToolAnnotations(server, expectedToolCount, errors) {
  if (expectedToolCount === 0) {
    errors.push("src/server.ts must register at least one tool");
    return;
  }

  requirePatternCount(
    server,
    /\bannotations\s*:\s*{/g,
    expectedToolCount,
    "src/server.ts must define annotations for every tool",
    errors
  );

  const requiredBooleanHints = [
    ["readOnlyHint", "read/write intent"],
    ["destructiveHint", "destructive action intent"],
    ["openWorldHint", "external world access intent"],
    ["idempotentHint", "repeat-call safety intent"],
  ];

  for (const [field, label] of requiredBooleanHints) {
    requirePatternCount(
      server,
      new RegExp("\\b" + field + "\\s*:\\s*(?:true|false)\\b", "g"),
      expectedToolCount,
      "src/server.ts must explicitly set `" + field + "` " + label + " on every tool",
      errors
    );
  }
}

function validateWidgetActionMetadata(server, errors) {
  requireString(server, "ui: { resourceUri: WIDGET_URI }", "widget tool _meta", errors);
  requireString(server, '"openai/toolInvocation/invoking"', "widget tool _meta", errors);
  requireString(server, '"openai/toolInvocation/invoked"', "widget tool _meta", errors);

  requirePatternCount(
    server,
    /["']openai\/outputTemplate["']\s*:\s*WIDGET_URI/g,
    2,
    "widget src/server.ts must set `openai/outputTemplate` on both the tool config and result _meta",
    errors
  );

  const widgetResourceMetadata = [
    "RESOURCE_MIME_TYPE",
    "_meta",
    "prefersBorder",
    "permissions",
    "csp",
    "connectDomains",
    "resourceDomains",
    '"openai/widgetDescription"',
  ];
  for (const needle of widgetResourceMetadata) {
    requireString(server, needle, "widget resource metadata", errors);
  }
}

function collectFiles(root, relativeDir = "") {
  const dir = path.join(root, relativeDir);
  if (!existsSync(dir)) {
    return [];
  }

  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "dist") {
      continue;
    }
    const relativePath = path.join(relativeDir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectFiles(root, relativePath));
      continue;
    }
    if (entry.isFile()) {
      files.push(relativePath);
    }
  }
  return files;
}

function rejectPlaceholders(root, errors) {
  for (const relativePath of collectFiles(root)) {
    if (/\.bundle\.(?:js|mjs|cjs)$/.test(relativePath)) {
      continue;
    }
    if (!/\.(json|md|ts|html|js|mjs|css)$/.test(relativePath)) {
      continue;
    }
    const text = readText(path.join(root, relativePath));
    for (const pattern of SECRET_PATTERNS) {
      if (text.includes(pattern)) {
        errors.push(relativePath + " contains forbidden placeholder or secret pattern `" + pattern + "`");
      }
    }
  }
}

function validatePackage(root, hasWidget, isCodexPlugin, errors) {
  const packagePath = requireFile(root, "package.json", errors);
  if (!packagePath) {
    return;
  }

  const pkg = readJson(packagePath, errors);
  if (!pkg) {
    return;
  }

  if (pkg.type !== "module") {
    errors.push("package.json must set type to module");
  }

  const expectedStart = isCodexPlugin ? "node mcp/server.bundle.mjs" : "tsx src/server.ts";
  if (!pkg.scripts || pkg.scripts.start !== expectedStart) {
    errors.push("package.json must define scripts.start as `" + expectedStart + "`");
  }

  if (!pkg.scripts || pkg.scripts.check !== "tsc --noEmit") {
    errors.push("package.json must define scripts.check as `tsc --noEmit`");
  }

  const dependencies = pkg.dependencies || {};
  if (!dependencies["@modelcontextprotocol/sdk"]) {
    errors.push("package.json must depend on @modelcontextprotocol/sdk");
  }
  if (!dependencies.zod) {
    errors.push("package.json must depend on zod");
  }
  if (hasWidget && !dependencies["@modelcontextprotocol/ext-apps"]) {
    errors.push("widget scaffolds must depend on @modelcontextprotocol/ext-apps");
  }

  const devDependencies = pkg.devDependencies || {};
  if (!devDependencies.typescript || !devDependencies.tsx || !devDependencies["@types/node"]) {
    errors.push("package.json must include TypeScript, tsx, and @types/node dev dependencies");
  }
  if (isCodexPlugin) {
    if (!pkg.scripts.build || !pkg.scripts.build.includes("mcp/server.bundle.mjs")) {
      errors.push("Codex plugin package.json must build mcp/server.bundle.mjs");
    }
    if (pkg.scripts.prepare !== "npm run build") {
      errors.push("Codex plugin package.json must build its runtime bundle during npm install");
    }
    if (!devDependencies.esbuild) {
      errors.push("Codex plugin package.json must include esbuild");
    }
  }
}

function validateServer(root, hasWidget, isCodexPlugin, errors) {
  const serverPath = requireFile(root, "src/server.ts", errors);
  if (!serverPath) {
    return;
  }

  const server = readText(serverPath);
  const required = [
    ["/mcp", "src/server.ts"],
    ["StreamableHTTPServerTransport", "src/server.ts"],
    ["outputSchema", "src/server.ts"],
    ["structuredContent", "src/server.ts"],
    // Connect-readiness contract: env-configurable port + JSON readiness probe.
    ["process.env.PORT", "src/server.ts"],
    ["/healthz", "src/server.ts"],
  ];

  for (const [needle, label] of required) {
    requireString(server, needle, label, errors);
  }

  if (!server.includes("content: [")) {
    errors.push("src/server.ts must return content alongside structuredContent");
  }

  const registeredToolCount =
    countMatches(server, /\bserver\.registerTool\s*\(/g) +
    countMatches(server, /\bregisterAppTool\s*\(/g);
  validateToolAnnotations(server, registeredToolCount, errors);

  if (hasWidget) {
    const widgetRequired = [
      "registerAppResource",
      "registerAppTool",
      "RESOURCE_MIME_TYPE",
      "_meta",
      "resourceUri",
      // Complete widget metadata / CSP shape for Codex render.
      "csp",
    ];
    for (const needle of widgetRequired) {
      requireString(server, needle, "widget src/server.ts", errors);
    }
    validateWidgetActionMetadata(server, errors);
  } else {
    requireString(server, "registerTool", "src/server.ts", errors);
  }

  if (isCodexPlugin) {
    requireString(server, "StdioServerTransport", "Codex plugin src/server.ts", errors);
    requireString(server, '--stdio', "Codex plugin src/server.ts", errors);
  }
}

function validateCodexPlugin(root, errors) {
  const manifestPath = requireFile(root, ".codex-plugin/plugin.json", errors);
  const mcpPath = requireFile(root, ".mcp.json", errors);
  requireFile(root, "mcp/server.bundle.mjs", errors);
  if (!manifestPath || !mcpPath) {
    return;
  }

  const manifest = readJson(manifestPath, errors);
  const mcp = readJson(mcpPath, errors);
  if (!manifest || !mcp) {
    return;
  }
  if (manifest.mcpServers !== "./.mcp.json") {
    errors.push("Codex plugin manifest must point mcpServers at ./.mcp.json");
  }
  const entries = mcp.mcpServers && typeof mcp.mcpServers === "object" ? mcp.mcpServers : {};
  if (Object.keys(entries).length !== 1) {
    errors.push(".mcp.json must define exactly one generated MCP server");
  }
  for (const [key, entry] of Object.entries(entries)) {
    if (entry?.command !== "node") {
      errors.push("mcpServers." + key + " must use the bundled Node launcher");
    }
    if (
      !Array.isArray(entry?.args) ||
      !entry.args.includes("${CLAUDE_PLUGIN_ROOT}/mcp/server.bundle.mjs") ||
      !entry.args.includes("--stdio")
    ) {
      errors.push("mcpServers." + key + " must launch the bundled server over stdio");
    }
  }

  if (manifest.apps) {
    if (manifest.apps !== "./.app.json") {
      errors.push("Codex plugin manifest apps field must point at ./.app.json");
    }
    const appPath = requireFile(root, ".app.json", errors);
    const appManifest = appPath ? readJson(appPath, errors) : null;
    const apps = appManifest?.apps && typeof appManifest.apps === "object" ? appManifest.apps : {};
    if (Object.keys(apps).length !== 1) {
      errors.push(".app.json must define exactly one generated app");
    }
    for (const [key, app] of Object.entries(apps)) {
      if (!isPluginAppId(app?.id)) {
        errors.push(
          "apps." + key + ".id must be a plugin_asdk_app_... id (legacy asdk_app_... is accepted)"
        );
      }
    }
  }
}

function validateWidget(root, errors) {
  const widgetPath = path.join(root, "public/widget.html");
  if (!existsSync(widgetPath)) {
    return false;
  }

  const widget = readText(widgetPath);
  const required = [
    "ui/initialize",
    "ui/notifications/initialized",
    "ui/notifications/tool-result",
    "tools/call",
    "ui/message",
    "window.openai",
    // Render cleanly inside the host's themed iframe.
    "background: transparent",
    "var(--color-",
  ];

  for (const needle of required) {
    requireString(widget, needle, "public/widget.html", errors);
  }

  return true;
}

function validateReadme(root, errors) {
  const readmePath = requireFile(root, "README.md", errors);
  if (!readmePath) {
    return;
  }
  const readme = readText(readmePath);
  requireString(readme, "Archetype:", "README.md", errors);
  requireString(readme, "npm run check", "README.md", errors);
}

function main() {
  const target = process.argv[2];
  if (!target || target === "--help" || target === "-h") {
    console.log(usage());
    process.exit(target ? 0 : 1);
  }

  const root = path.resolve(target);
  const errors = [];

  if (!existsSync(root) || !statSync(root).isDirectory()) {
    errors.push("App directory does not exist: " + root);
  } else {
    requireFile(root, "tsconfig.json", errors);
    const isCodexPlugin = existsSync(path.join(root, ".codex-plugin", "plugin.json"));
    const hasWidget = validateWidget(root, errors);
    validatePackage(root, hasWidget, isCodexPlugin, errors);
    validateServer(root, hasWidget, isCodexPlugin, errors);
    if (isCodexPlugin) {
      validateCodexPlugin(root, errors);
    }
    validateReadme(root, errors);
    rejectPlaceholders(root, errors);
  }

  if (errors.length > 0) {
    console.error("Scaffold validation failed:");
    for (const error of errors) {
      console.error("- " + error);
    }
    process.exit(1);
  }

  console.log("Scaffold validation passed");
}

main();
