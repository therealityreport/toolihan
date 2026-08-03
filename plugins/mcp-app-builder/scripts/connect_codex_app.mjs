#!/usr/bin/env node

// Orchestrator that closes the loop from "scaffold" to "connected in Codex".
//
//   up     scaffold (optional) -> npm install -> allocate free port ->
//          start server (detached, PID/log tracked) -> wait for /healthz ->
//          verify MCP connection -> (fail-closed) register with `codex mcp add`
//          -> (apps-app mode) record app metadata + backend-publish guidance.
//   down   stop the tracked server, unregister from Codex (or restore config).
//   status re-check the tracked server + registration.
//
// Fully automated by design (no prompts), but never destructive: config.toml is
// backed up before any mutation, registration only happens after verification
// passes, and teardown only kills processes this tool started.
//
// Modes:
//   mcp-server (default) — tools AND widgets are usable in Codex CLI + Codex.app
//                          via the registered MCP server. No backend account step.
//   apps-app             — everything in mcp-server, plus records .mcp.json app
//                          metadata and prints how to publish a discoverable
//                          `asdk_app_...` connector (a ChatGPT-side step that is
//                          NOT required to use the app locally, and whose id is
//                          never fabricated here).

import {
  appendFileSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  openSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const CODEX_CONFIG = path.join(os.homedir(), ".codex", "config.toml");

function toSlug(value) {
  const normalized = String(value)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || "example-mcp-app";
}

function shortHash(value) {
  // Small deterministic suffix to disambiguate same-slug apps at different paths.
  let hash = 5381;
  for (const ch of String(value)) {
    hash = ((hash << 5) + hash + ch.charCodeAt(0)) >>> 0;
  }
  return hash.toString(36).slice(0, 6);
}

function stateDir(appDir) {
  return path.join(appDir, ".mcp-app");
}

function statePath(appDir) {
  return path.join(stateDir(appDir), "state.json");
}

function readState(appDir) {
  const file = statePath(appDir);
  if (!existsSync(file)) {
    return null;
  }
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

function writeState(appDir, state) {
  mkdirSync(stateDir(appDir), { recursive: true });
  writeFileSync(statePath(appDir), JSON.stringify(state, null, 2) + "\n", "utf8");
}

function logRun(appDir, phase, status, detail) {
  try {
    mkdirSync(stateDir(appDir), { recursive: true });
    const line = JSON.stringify({
      ts: new Date().toISOString(),
      phase,
      status,
      detail: detail ?? null,
    });
    appendFileSync(path.join(stateDir(appDir), "run.log"), line + "\n", "utf8");
  } catch {
    // logging must never break the run
  }
}

function checkPortFree(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once("error", () => resolve(false));
    server.once("listening", () => server.close(() => resolve(true)));
    server.listen(port, "127.0.0.1");
  });
}

async function allocatePort(preferred, avoid) {
  let candidate = preferred;
  for (let i = 0; i < 200; i += 1) {
    if (!avoid.has(candidate) && (await checkPortFree(candidate))) {
      return candidate;
    }
    candidate += 1;
  }
  throw new Error("Could not find a free port near " + preferred);
}

function occupiedPortsFromSiblings(appDir) {
  // Avoid ports recorded by other apps' state files under the same parent dir.
  const avoid = new Set();
  const parent = path.dirname(appDir);
  if (!existsSync(parent)) {
    return avoid;
  }
  for (const entry of readdirSync(parent, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }
    const sibling = path.join(parent, entry.name);
    if (sibling === appDir) {
      continue;
    }
    const state = readState(sibling);
    if (state && Number.isInteger(state.port)) {
      avoid.add(state.port);
    }
  }
  return avoid;
}

function defaultPortFromEnvExample(appDir) {
  const file = path.join(appDir, ".env.example");
  if (existsSync(file)) {
    const match = readFileSync(file, "utf8").match(/^PORT=(\d+)/m);
    if (match) {
      return Number(match[1]);
    }
  }
  return 8787;
}

async function waitForHealth(baseUrl, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let lastError = "no response";
  while (Date.now() < deadline) {
    try {
      const res = await fetch(baseUrl + "/healthz");
      if (res.ok) {
        return { ok: true, body: await res.json().catch(() => null) };
      }
      lastError = "HTTP " + res.status;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
    await new Promise((resolve) => setTimeout(resolve, 400));
  }
  return { ok: false, error: lastError };
}

function isAlive(pid) {
  if (!pid) {
    return false;
  }
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function runCodex(args) {
  const result = spawnSync("codex", args, { encoding: "utf8" });
  return {
    status: result.status,
    stdout: (result.stdout ?? "").trim(),
    stderr: (result.stderr ?? "").trim(),
    error: result.error ? result.error.message : null,
  };
}

function runNode(scriptName, args, cwd) {
  const result = spawnSync("node", [path.join(SCRIPT_DIR, scriptName), ...args], {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  return {
    status: result.status,
    stdout: (result.stdout ?? "").trim(),
    stderr: (result.stderr ?? "").trim(),
  };
}

function backupConfig() {
  if (!existsSync(CODEX_CONFIG)) {
    return null;
  }
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const backup = CODEX_CONFIG + ".bak." + ts;
  copyFileSync(CODEX_CONFIG, backup);
  return backup;
}

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const args = {
    command,
    app: null,
    name: null,
    archetype: "vanilla-widget",
    target: "standalone",
    appId: null,
    marketplace: null,
    toolName: null,
    mode: "mcp-server",
    port: null,
    scaffold: false,
    reinstall: false,
    call: false,
    force: false,
    purge: false,
    restoreConfig: false,
    timeout: 20000,
    json: false,
  };
  const tokens = [...rest];
  const takeValue = (flag) => {
    const value = tokens.shift();
    if (value === undefined || value.startsWith("--")) {
      fail("Expected a value after " + flag);
    }
    return value;
  };
  while (tokens.length > 0) {
    const token = tokens.shift();
    switch (token) {
      case "--app":
        args.app = takeValue(token);
        break;
      case "--name":
        args.name = takeValue(token);
        break;
      case "--archetype":
        args.archetype = takeValue(token);
        break;
      case "--target":
        args.target = takeValue(token);
        break;
      case "--app-id":
        args.appId = takeValue(token);
        break;
      case "--marketplace":
        args.marketplace = takeValue(token);
        break;
      case "--tool-name":
        args.toolName = takeValue(token);
        break;
      case "--mode":
        args.mode = takeValue(token);
        break;
      case "--port":
        args.port = Number(takeValue(token));
        break;
      case "--scaffold":
        args.scaffold = true;
        break;
      case "--reinstall":
        args.reinstall = true;
        break;
      case "--call":
        args.call = true;
        break;
      case "--force":
        args.force = true;
        break;
      case "--purge":
        args.purge = true;
        break;
      case "--restore-config":
        args.restoreConfig = true;
        break;
      case "--timeout":
        args.timeout = Number(takeValue(token));
        break;
      case "--json":
        args.json = true;
        break;
      default:
        fail("Unknown argument: " + token);
    }
  }
  if (!["mcp-server", "apps-app"].includes(args.mode)) {
    fail("--mode must be mcp-server or apps-app");
  }
  if (!["standalone", "codex-plugin"].includes(args.target)) {
    fail("--target must be standalone or codex-plugin");
  }
  if (args.target === "codex-plugin" && args.mode === "apps-app") {
    fail("--mode apps-app would overwrite the generated plugin launcher; use --mode mcp-server");
  }
  return args;
}

function usage() {
  return [
    "Connect a generated MCP app to Codex (Codex CLI + Codex.app), fully automated.",
    "",
    "Usage:",
    "  node scripts/connect_codex_app.mjs up   --app <dir> [--name <n> --archetype <a>] [--target standalone|codex-plugin] [--mode mcp-server|apps-app]",
    "  node scripts/connect_codex_app.mjs down --app <dir> [--restore-config] [--purge]",
    "  node scripts/connect_codex_app.mjs status --app <dir>",
    "",
    "up options:",
    "  --app <dir>       App directory (scaffolded into if empty + --name/--scaffold given).",
    "  --name <name>     App name (required to scaffold a new app).",
    "  --archetype <a>   tool-only | vanilla-widget | interactive-decoupled (default vanilla-widget).",
    "  --target <t>      standalone (default) or codex-plugin.",
    "  --app-id <id>     Backend-issued plugin_asdk_app_... id for a Codex plugin target.",
    "  --marketplace <p> Add the generated plugin to this marketplace.json.",
    "  --tool-name <n>   Primary tool name override.",
    "  --mode <m>        mcp-server (default) or apps-app.",
    "  --port <n>        Preferred port (auto-allocated free port otherwise).",
    "  --reinstall       Force `npm install` even if node_modules exists.",
    "  --call            Exercise a tools/call during verification.",
    "  --force           Register even if verification fails (debugging).",
    "  --timeout <ms>    Readiness/verify timeout (default 20000).",
    "  --json            Structured JSON output.",
  ].join("\n");
}

function resolveAppDir(args) {
  if (args.app) {
    return path.resolve(args.app);
  }
  fail("Missing required --app <dir>.\n\n" + usage());
}

function scaffoldIfNeeded(appDir, args, report) {
  const hasProject = existsSync(path.join(appDir, "package.json"));
  const isEmpty = !existsSync(appDir) || readdirSync(appDir).length === 0;
  const wantScaffold = args.scaffold || (!hasProject && (isEmpty || args.name));
  if (!wantScaffold) {
    if (!hasProject) {
      fail(
        "No package.json in " +
          appDir +
          " and not scaffolding. Pass --name to scaffold a new app, or point --app at an existing app."
      );
    }
    return false;
  }
  const name = args.name || path.basename(appDir);
  const scaffoldArgs = [
    "--name",
    name,
    "--out",
    appDir,
    "--archetype",
    args.archetype,
    "--target",
    args.target,
  ];
  if (args.toolName) {
    scaffoldArgs.push("--tool-name", args.toolName);
  }
  if (args.appId) {
    scaffoldArgs.push("--app-id", args.appId);
  }
  if (args.marketplace) {
    scaffoldArgs.push("--marketplace", args.marketplace);
  }
  if (args.port) {
    scaffoldArgs.push("--port", String(args.port));
  }
  if (!isEmpty) {
    scaffoldArgs.push("--force");
  }
  const result = runNode("scaffold_node_app.mjs", scaffoldArgs, process.cwd());
  logRun(appDir, "scaffold", result.status === 0 ? "ok" : "fail", result.stderr || result.stdout);
  if (result.status !== 0) {
    fail("Scaffold failed: " + (result.stderr || result.stdout));
  }
  report.push("scaffolded " + args.archetype + " app at " + appDir);
  return true;
}

function ensureInstalled(appDir, args, report) {
  const hasModules = existsSync(path.join(appDir, "node_modules"));
  if (hasModules && !args.reinstall) {
    return;
  }
  report.push(hasModules ? "reinstalling dependencies" : "installing dependencies");
  const result = spawnSync("npm", ["install", "--no-audit", "--no-fund"], {
    cwd: appDir,
    encoding: "utf8",
  });
  logRun(appDir, "install", result.status === 0 ? "ok" : "fail", (result.stderr ?? "").trim().slice(-400));
  if (result.status !== 0) {
    fail("npm install failed: " + (result.stderr ?? "").trim().slice(-400));
  }
}

function startServer(appDir, port) {
  mkdirSync(stateDir(appDir), { recursive: true });
  const outPath = path.join(stateDir(appDir), "server.log");
  const errPath = path.join(stateDir(appDir), "server.err");
  const out = openSync(outPath, "a");
  const err = openSync(errPath, "a");
  const child = spawn("npm", ["start"], {
    cwd: appDir,
    detached: true,
    env: { ...process.env, PORT: String(port) },
    stdio: ["ignore", out, err],
  });
  child.unref();
  writeFileSync(path.join(stateDir(appDir), "server.pid"), String(child.pid) + "\n", "utf8");
  return child.pid;
}

function stopProcessGroup(pid) {
  if (!pid || !isAlive(pid)) {
    return false;
  }
  try {
    // Server was started detached (its own process group); negative pid kills
    // the whole group (npm + tsx child).
    process.kill(-pid, "SIGTERM");
  } catch {
    try {
      process.kill(pid, "SIGTERM");
    } catch {
      // already gone
    }
  }
  return true;
}

async function cmdUp(args) {
  const appDir = resolveAppDir(args);
  const report = [];

  scaffoldIfNeeded(appDir, args, report);

  // Idempotency: if a live server is already tracked and healthy, re-verify only.
  const prior = readState(appDir);
  const slug = toSlug(args.name || path.basename(appDir));
  const serverName = prior?.serverName || "mcpab_" + slug;

  ensureInstalled(appDir, args, report);

  // Port allocation.
  const avoid = occupiedPortsFromSiblings(appDir);
  const preferred = args.port || prior?.port || defaultPortFromEnvExample(appDir);
  const port =
    prior && isAlive(prior.pid) && prior.port
      ? prior.port
      : await allocatePort(preferred, avoid);
  const baseUrl = "http://localhost:" + port;
  const mcpUrl = baseUrl + "/mcp";

  // Start (or reuse) the server.
  let pid = prior?.pid;
  if (isAlive(pid) && prior?.port === port) {
    report.push("reusing running server pid=" + pid + " on port " + port);
  } else {
    pid = startServer(appDir, port);
    report.push("started server pid=" + pid + " on port " + port);
  }
  logRun(appDir, "start", "ok", { pid, port });

  // Readiness.
  const health = await waitForHealth(baseUrl, args.timeout);
  if (!health.ok) {
    logRun(appDir, "health", "fail", health.error);
    const errTail = tailFile(path.join(stateDir(appDir), "server.err"), 8);
    fail(
      "Server did not become ready at " +
        baseUrl +
        "/healthz within " +
        args.timeout +
        "ms: " +
        health.error +
        (errTail ? "\n--- server.err ---\n" + errTail : "")
    );
  }
  report.push("health ok");
  logRun(appDir, "health", "ok", health.body);

  // Verification gate (fail-closed).
  const verifyArgs = ["--app", appDir, "--port", String(port), "--json"];
  if (args.call) {
    verifyArgs.push("--call");
  }
  const verify = runNode("verify_codex_connection.mjs", verifyArgs, process.cwd());
  let verifyReport = null;
  try {
    verifyReport = JSON.parse(verify.stdout);
  } catch {
    verifyReport = { ok: verify.status === 0, raw: verify.stdout || verify.stderr };
  }
  logRun(appDir, "verify", verifyReport.ok ? "ok" : "fail", verifyReport.checks ?? verifyReport.raw);
  if (!verifyReport.ok && !args.force) {
    // Do NOT touch Codex config if the app doesn't actually work.
    writeState(appDir, {
      ...(prior || {}),
      slug,
      serverName,
      appDir,
      archetype: detectArchetype(appDir, args.archetype),
      mode: args.mode,
      port,
      pid,
      mcpUrl,
      registered: false,
      verified: false,
      startedAt: prior?.startedAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    fail(
      "Verification failed — not registering with Codex (fail-closed). " +
        "Re-run with --force to override.\n" +
        JSON.stringify(verifyReport.checks ?? verifyReport, null, 2)
    );
  }
  report.push(verifyReport.ok ? "verification passed" : "verification FAILED (registering anyway due to --force)");

  // Register with Codex (idempotent upsert): back up config, remove old, add new.
  const configBackup = backupConfig();
  runCodex(["mcp", "remove", serverName]); // ignore if absent
  const add = runCodex(["mcp", "add", serverName, "--url", mcpUrl]);
  if (add.status !== 0) {
    logRun(appDir, "register", "fail", add.stderr || add.error);
    fail(
      "`codex mcp add` failed: " +
        (add.stderr || add.error || "unknown") +
        (configBackup ? "\nconfig backup at " + configBackup : "")
    );
  }
  report.push("registered MCP server `" + serverName + "` -> " + mcpUrl);
  logRun(appDir, "register", "ok", { serverName, mcpUrl, configBackup });

  // apps-app mode: record local app metadata + backend-publish guidance.
  let appsAppNote = null;
  if (args.mode === "apps-app") {
    writeMcpJson(appDir, serverName, mcpUrl);
    appsAppNote =
      "apps-app mode: recorded .mcp.json. The app is fully usable in Codex now (tools + widget). " +
      "A DISCOVERABLE `asdk_app_...` connector is a separate ChatGPT-side publishing step — its id " +
      "is backend/account-issued and is not created here. To pursue it later, use " +
      "recreate_mcp_apps_from_urls.mjs; never hand-write an app id.";
    report.push("apps-app: wrote .mcp.json + publish guidance");
    logRun(appDir, "apps-app", "ok", "wrote .mcp.json");
  }

  const state = {
    slug,
    serverName,
    appDir,
    archetype: detectArchetype(appDir, args.archetype),
    mode: args.mode,
    port,
    pid,
    mcpUrl,
    registered: true,
    verified: verifyReport.ok,
    configBackup,
    startedAt: prior?.startedAt || new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  writeState(appDir, state);

  return output(args, {
    ok: true,
    command: "up",
    ...state,
    verify: verifyReport.checks ?? verifyReport,
    notes: appsAppNote ? [appsAppNote] : [],
    report,
    hint:
      "Codex CLI picks up the server on its next session. In Codex.app, reload/restart to see it. " +
      "Tear down with: node scripts/connect_codex_app.mjs down --app " + appDir,
  });
}

async function cmdDown(args) {
  const appDir = resolveAppDir(args);
  const state = readState(appDir);
  if (!state) {
    return output(args, { ok: true, command: "down", note: "no state.json — nothing to stop." });
  }
  const report = [];

  // Stop the server we started.
  if (stopProcessGroup(state.pid)) {
    // give it a moment, then escalate
    await new Promise((resolve) => setTimeout(resolve, 800));
    if (isAlive(state.pid)) {
      try {
        process.kill(-state.pid, "SIGKILL");
      } catch {
        try {
          process.kill(state.pid, "SIGKILL");
        } catch {
          // gone
        }
      }
    }
    report.push("stopped server pid=" + state.pid);
  } else {
    report.push("server pid=" + (state.pid ?? "?") + " not running");
  }
  logRun(appDir, "stop", "ok", state.pid);

  // Confirm the port is released.
  if (state.port) {
    const free = await checkPortFree(state.port);
    report.push(free ? "port " + state.port + " released" : "warning: port " + state.port + " still bound");
  }

  // Unregister from Codex (or restore the pre-registration backup).
  if (args.restoreConfig && state.configBackup && existsSync(state.configBackup)) {
    copyFileSync(state.configBackup, CODEX_CONFIG);
    report.push("restored config from " + state.configBackup);
  } else if (state.serverName) {
    const remove = runCodex(["mcp", "remove", state.serverName]);
    report.push(
      remove.status === 0
        ? "removed MCP server `" + state.serverName + "`"
        : "codex mcp remove reported: " + (remove.stderr || remove.error || "non-zero")
    );
  }
  logRun(appDir, "unregister", "ok", state.serverName);

  // Clean runtime files.
  const pidFile = path.join(stateDir(appDir), "server.pid");
  if (existsSync(pidFile)) {
    rmSync(pidFile);
  }
  writeState(appDir, { ...state, pid: null, registered: false, updatedAt: new Date().toISOString() });
  if (args.purge) {
    rmSync(stateDir(appDir), { recursive: true, force: true });
    report.push("purged .mcp-app/");
  }

  return output(args, { ok: true, command: "down", serverName: state.serverName, report });
}

async function cmdStatus(args) {
  const appDir = resolveAppDir(args);
  const state = readState(appDir);
  if (!state) {
    return output(args, { ok: false, command: "status", note: "no state.json for " + appDir });
  }
  const alive = isAlive(state.pid);
  let health = null;
  if (state.port) {
    const res = await waitForHealth("http://localhost:" + state.port, 1500);
    health = res.ok ? res.body : { error: res.error };
  }
  const registered = state.serverName ? runCodex(["mcp", "get", state.serverName]) : null;
  return output(args, {
    ok: alive,
    command: "status",
    serverName: state.serverName,
    mode: state.mode,
    port: state.port,
    pid: state.pid,
    alive,
    health,
    mcpUrl: state.mcpUrl,
    registeredInCodex: registered ? registered.status === 0 : null,
  });
}

function detectArchetype(appDir, fallback) {
  if (existsSync(path.join(appDir, "public", "widget.html"))) {
    return fallback && fallback !== "tool-only" ? fallback : "vanilla-widget";
  }
  return "tool-only";
}

function writeMcpJson(appDir, serverName, mcpUrl) {
  const file = path.join(appDir, ".mcp.json");
  const payload = {
    mcpServers: {
      [serverName]: { type: "http", url: mcpUrl },
    },
  };
  writeFileSync(file, JSON.stringify(payload, null, 2) + "\n", "utf8");
}

function tailFile(file, lines) {
  if (!existsSync(file)) {
    return "";
  }
  const content = readFileSync(file, "utf8").trimEnd().split("\n");
  return content.slice(-lines).join("\n");
}

function output(args, payload) {
  if (args.json) {
    console.log(JSON.stringify(payload, null, 2));
  } else {
    const lines = [];
    lines.push((payload.ok ? "OK" : "FAILED") + " — " + payload.command);
    if (payload.report) {
      for (const item of payload.report) {
        lines.push("  - " + item);
      }
    }
    if (payload.serverName) lines.push("  server: " + payload.serverName);
    if (payload.mcpUrl) lines.push("  url: " + payload.mcpUrl);
    if (payload.mode) lines.push("  mode: " + payload.mode);
    if (payload.alive !== undefined) lines.push("  alive: " + payload.alive);
    if (payload.health) lines.push("  health: " + JSON.stringify(payload.health));
    if (payload.notes) {
      for (const note of payload.notes) {
        lines.push("  note: " + note);
      }
    }
    if (payload.hint) lines.push("  " + payload.hint);
    if (payload.note) lines.push("  " + payload.note);
    console.log(lines.join("\n"));
  }
  process.exit(payload.ok ? 0 : 1);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.command || args.command === "--help" || args.command === "-h") {
    console.log(usage());
    process.exit(args.command ? 0 : 1);
  }
  switch (args.command) {
    case "up":
      await cmdUp(args);
      break;
    case "down":
      await cmdDown(args);
      break;
    case "status":
      await cmdStatus(args);
      break;
    default:
      fail("Unknown command `" + args.command + "`.\n\n" + usage());
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
