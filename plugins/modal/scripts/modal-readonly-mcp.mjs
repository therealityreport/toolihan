#!/usr/bin/env node

import { execFile } from "node:child_process";
import readline from "node:readline";
import { pathToFileURL } from "node:url";

const SERVER_NAME = "modal-readonly";
const SERVER_VERSION = "1.1.0";
const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_MAX_BUFFER = 512 * 1024;
const LOG_OUTPUT_LIMIT = 256 * 1024;

const ERROR_CODES = new Set([
  "CLI_NOT_FOUND",
  "AUTH_REQUIRED",
  "INVALID_INPUT",
  "APP_NOT_FOUND",
  "AMBIGUOUS_APP",
  "TIMEOUT",
  "CLI_FAILED",
  "MALFORMED_OUTPUT",
  "OUTPUT_LIMIT",
]);

const SOURCE_VALUES = new Set(["stdout", "stderr", "system"]);
const ID_PATTERNS = {
  app: /^ap-[A-Za-z0-9_-]+$/,
  function: /^fu-[A-Za-z0-9_-]+$/,
  functionCall: /^fc-[A-Za-z0-9_-]+$/,
  container: /^(?:ta|ct)-[A-Za-z0-9_-]+$/,
};
const ENVIRONMENT_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const APP_NAME_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._ -]{0,255}$/;
const RELATIVE_TIME_PATTERN = /^\d+(?:s|m|h|d|w)$/;

function schema(properties, required = []) {
  return { type: "object", additionalProperties: false, properties, required };
}

export const TOOLS = [
  {
    name: "modal_identity",
    description: "Return the installed Modal CLI version and active profile label without changing authentication or profile state.",
    inputSchema: schema({}),
  },
  {
    name: "modal_apps_list",
    description: "List Modal apps in an explicit environment using the read-only JSON CLI surface.",
    inputSchema: schema({
      environment: { type: "string", minLength: 1, maxLength: 128 },
      limit: { type: "integer", minimum: 1, maximum: 200, default: 50 },
    }, ["environment"]),
  },
  {
    name: "modal_app_history",
    description: "Return bounded deployment history for an exact app ID or a uniquely resolved app name.",
    inputSchema: schema({
      environment: { type: "string", minLength: 1, maxLength: 128 },
      app: { type: "string", minLength: 1, maxLength: 256 },
      limit: { type: "integer", minimum: 1, maximum: 100, default: 20 },
    }, ["environment", "app"]),
  },
  {
    name: "modal_app_logs",
    description: "Fetch non-following, time-bounded Modal app logs with strict output and timeout limits.",
    inputSchema: schema({
      environment: { type: "string", minLength: 1, maxLength: 128 },
      app: { type: "string", minLength: 1, maxLength: 256 },
      since: { type: "string", default: "1h" },
      until: { type: "string" },
      tail: { type: "integer", minimum: 1, maximum: 500, default: 100 },
      source: { type: "string", enum: ["stdout", "stderr", "system"] },
      search: { type: "string", maxLength: 256 },
      functionId: { type: "string" },
      functionCallId: { type: "string" },
      containerId: { type: "string" },
    }, ["environment", "app"]),
  },
  {
    name: "modal_containers_list",
    description: "List running Modal containers in an explicit environment, optionally restricted to one app.",
    inputSchema: schema({
      environment: { type: "string", minLength: 1, maxLength: 128 },
      app: { type: "string", minLength: 1, maxLength: 256 },
      limit: { type: "integer", minimum: 1, maximum: 500, default: 100 },
    }, ["environment"]),
  },
];

const TOOL_NAMES = new Set(TOOLS.map((tool) => tool.name));

class ModalMcpError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = "ModalMcpError";
    this.code = ERROR_CODES.has(code) ? code : "CLI_FAILED";
    this.details = details;
  }
}

function integer(value, name, fallback, maximum) {
  if (value === undefined) return fallback;
  if (!Number.isInteger(value) || value < 1 || value > maximum) {
    throw new ModalMcpError("INVALID_INPUT", `${name} must be an integer from 1 through ${maximum}.`);
  }
  return value;
}

function requiredString(value, name, pattern, maximum = 256) {
  if (typeof value !== "string" || value.length < 1 || value.length > maximum || (pattern && !pattern.test(value))) {
    throw new ModalMcpError("INVALID_INPUT", `${name} is invalid.`);
  }
  return value;
}

function optionalString(value, name, pattern, maximum = 256) {
  if (value === undefined) return undefined;
  return requiredString(value, name, pattern, maximum);
}

function timeValue(value, name, fallback) {
  if (value === undefined) return fallback;
  if (typeof value !== "string" || value.length > 64) throw new ModalMcpError("INVALID_INPUT", `${name} is invalid.`);
  if (RELATIVE_TIME_PATTERN.test(value)) return value;
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) throw new ModalMcpError("INVALID_INPUT", `${name} must be a relative duration or ISO timestamp.`);
  return value;
}

function environment(value) {
  return requiredString(value, "environment", ENVIRONMENT_PATTERN, 128);
}

function appIdentifier(value) {
  if (typeof value !== "string" || value.length > 256) throw new ModalMcpError("INVALID_INPUT", "app is invalid.");
  if (ID_PATTERNS.app.test(value)) return value;
  return requiredString(value, "app", APP_NAME_PATTERN, 256);
}

function minimalEnvironment() {
  const allowed = [
    "PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "XDG_CONFIG_HOME",
    "MODAL_PROFILE", "MODAL_ENVIRONMENT", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE",
    "MODAL_CLI", "MODAL_MCP_TIMEOUT_MS", "MODAL_MCP_MAX_BUFFER",
    "FAKE_MODAL_MODE", "FAKE_MODAL_LOG",
  ];
  return Object.fromEntries(allowed.filter((key) => process.env[key] !== undefined).map((key) => [key, process.env[key]]));
}

export function assertAllowedCommand(args) {
  if (!Array.isArray(args) || args.some((value) => typeof value !== "string" || value.includes("\0"))) {
    throw new ModalMcpError("INVALID_INPUT", "Invalid Modal CLI argument array.");
  }
  if (args.length === 1 && args[0] === "--version") return true;
  if (args.length === 2 && args[0] === "profile" && args[1] === "current") return true;

  const [group, action] = args;
  const permitted = (group === "app" && ["list", "history", "logs"].includes(action))
    || (group === "container" && action === "list");
  if (!permitted) throw new ModalMcpError("INVALID_INPUT", "Modal CLI command is not in the read-only allowlist.");

  const mutationTokens = new Set([
    "deploy", "run", "rollback", "rollover", "stop", "exec", "secret", "token",
    "setup", "activate", "create", "delete", "update", "shell", "serve",
  ]);
  if (args.some((value) => mutationTokens.has(value))) {
    throw new ModalMcpError("INVALID_INPUT", "Mutation-capable Modal CLI command is forbidden.");
  }

  const allowedFlags = new Set([
    "--env", "--json", "--since", "--until", "--tail", "--search", "--function",
    "--function-call", "--container", "--source", "--timestamps", "--show-function-id",
    "--show-function-call-id", "--show-container-id", "--app-id",
  ]);
  for (let index = 2; index < args.length; index += 1) {
    const value = args[index];
    if (!value.startsWith("--")) continue;
    if (!allowedFlags.has(value)) throw new ModalMcpError("INVALID_INPUT", `Modal CLI flag ${value} is not allowed.`);
    if (!["--json", "--timestamps", "--show-function-id", "--show-function-call-id", "--show-container-id"].includes(value)) index += 1;
  }
  if (args.includes("--follow") || args.includes("-f")) throw new ModalMcpError("INVALID_INPUT", "Following logs is forbidden.");
  return true;
}

export function redact(value) {
  let redacted = String(value ?? "")
    .replace(/\b(?:ak|sk|pk|tok|token)[-_][A-Za-z0-9._-]{12,}\b/gi, "[REDACTED_TOKEN]")
    .replace(/(authorization\s*[:=]\s*(?:bearer\s+)?)[^\s,;]+/gi, "$1[REDACTED]")
    .replace(/((?:api[_-]?key|token|secret|password)\s*[:=]\s*)[^\s,;]+/gi, "$1[REDACTED]");
  if (process.env.HOME) redacted = redacted.replaceAll(process.env.HOME, "$HOME");
  return redacted;
}

function classifyCliError(error, stderr) {
  const text = redact(stderr || error?.message || "Modal CLI failed.");
  if (error?.code === "ENOENT") return new ModalMcpError("CLI_NOT_FOUND", "The Modal CLI was not found.");
  if (error?.killed || error?.signal === "SIGTERM" || /timed out/i.test(text)) return new ModalMcpError("TIMEOUT", "The Modal CLI command timed out.");
  if (error?.code === "ERR_CHILD_PROCESS_STDIO_MAXBUFFER" || /maxbuffer/i.test(text)) return new ModalMcpError("OUTPUT_LIMIT", "The Modal CLI output exceeded the configured limit.");
  if (/auth|credential|token|log[ -]?in|sign[ -]?in|unauthorized|forbidden/i.test(text)) {
    return new ModalMcpError("AUTH_REQUIRED", "Modal authentication is unavailable. No login, refresh, repair, or retry was attempted.");
  }
  return new ModalMcpError("CLI_FAILED", text.slice(0, 2048));
}

export function runCli(args, options = {}) {
  assertAllowedCommand(args);
  const cli = process.env.MODAL_CLI || "modal";
  const timeout = Number(process.env.MODAL_MCP_TIMEOUT_MS || options.timeoutMs || DEFAULT_TIMEOUT_MS);
  const maxBuffer = Number(process.env.MODAL_MCP_MAX_BUFFER || options.maxBuffer || DEFAULT_MAX_BUFFER);
  return new Promise((resolve, reject) => {
    execFile(cli, args, {
      shell: false,
      timeout: Number.isFinite(timeout) && timeout > 0 ? timeout : DEFAULT_TIMEOUT_MS,
      maxBuffer: Number.isFinite(maxBuffer) && maxBuffer > 0 ? maxBuffer : DEFAULT_MAX_BUFFER,
      encoding: "utf8",
      windowsHide: true,
      env: minimalEnvironment(),
    }, (error, stdout, stderr) => {
      if (error) return reject(classifyCliError(error, stderr));
      resolve({ stdout: String(stdout || ""), stderr: String(stderr || "") });
    });
  });
}

function parseJson(stdout) {
  try {
    return JSON.parse(stdout);
  } catch {
    throw new ModalMcpError("MALFORMED_OUTPUT", "The Modal CLI returned malformed JSON.");
  }
}

function rows(value) {
  if (Array.isArray(value)) return value;
  for (const key of ["apps", "items", "data", "containers", "history", "deployments"]) {
    if (Array.isArray(value?.[key])) return value[key];
  }
  return [];
}

function field(row, names) {
  for (const name of names) if (row?.[name] !== undefined && row[name] !== null) return row[name];
  return null;
}

function normalizeApp(row) {
  return {
    appId: field(row, ["app_id", "appId", "id", "App ID"]),
    name: field(row, ["name", "app_name", "appName", "description", "Description"]),
    state: field(row, ["state", "status", "State"]),
    createdAt: field(row, ["created_at", "createdAt", "Created at"]),
    stoppedAt: field(row, ["stopped_at", "stoppedAt", "Stopped at"]),
  };
}

function normalizeHistory(row) {
  return {
    version: field(row, ["version", "version_id", "versionId", "Version"]),
    state: field(row, ["state", "status", "State"]),
    createdAt: field(row, ["created_at", "createdAt", "Created at"]),
    deployedAt: field(row, ["deployed_at", "deployedAt", "Deployed at"]),
    clientVersion: field(row, ["client_version", "clientVersion", "Client version"]),
  };
}

function normalizeContainer(row) {
  return {
    containerId: field(row, ["container_id", "containerId", "id", "Container ID"]),
    appId: field(row, ["app_id", "appId", "App ID"]),
    functionId: field(row, ["function_id", "functionId", "Function ID"]),
    taskId: field(row, ["task_id", "taskId", "Task ID"]),
    state: field(row, ["state", "status", "State"]),
    startedAt: field(row, ["started_at", "startedAt", "Started at"]),
  };
}

async function cliVersion() {
  const { stdout } = await runCli(["--version"]);
  return redact(stdout).trim().replace(/^modal client version:\s*/i, "") || "unknown";
}

async function listApps(env) {
  const { stdout } = await runCli(["app", "list", "--env", env, "--json"]);
  return rows(parseJson(stdout)).map(normalizeApp).filter((app) => app.appId || app.name);
}

async function resolveApp(env, requested) {
  const app = appIdentifier(requested);
  if (ID_PATTERNS.app.test(app)) return app;
  const matches = (await listApps(env)).filter((candidate) => candidate.name === app);
  if (matches.length === 0) throw new ModalMcpError("APP_NOT_FOUND", `No app named ${app} exists in the requested environment.`);
  if (matches.length > 1) throw new ModalMcpError("AMBIGUOUS_APP", `More than one app is named ${app}; use an exact app ID.`);
  if (!ID_PATTERNS.app.test(String(matches[0].appId || ""))) throw new ModalMcpError("MALFORMED_OUTPUT", "The resolved app did not include a valid app ID.");
  return matches[0].appId;
}

function envelope(data, meta = {}) {
  return { ok: true, data, meta: { truncated: false, ...meta } };
}

export async function callTool(name, input = {}) {
  if (!TOOL_NAMES.has(name)) throw new ModalMcpError("INVALID_INPUT", `Unknown tool: ${name}`);
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new ModalMcpError("INVALID_INPUT", "Tool input must be an object.");
  const started = Date.now();

  if (name === "modal_identity") {
    if (Object.keys(input).length) throw new ModalMcpError("INVALID_INPUT", "modal_identity accepts no input fields.");
    const version = await cliVersion();
    const { stdout } = await runCli(["profile", "current"]);
    return envelope({ clientVersion: version, activeProfile: redact(stdout).trim(), cliSource: process.env.MODAL_CLI ? "MODAL_CLI" : "PATH" }, { durationMs: Date.now() - started, clientVersion: version });
  }

  const env = environment(input.environment);
  if (name === "modal_apps_list") {
    const limit = integer(input.limit, "limit", 50, 200);
    const apps = await listApps(env);
    return envelope(apps.slice(0, limit), { environment: env, total: apps.length, truncated: apps.length > limit, durationMs: Date.now() - started });
  }

  if (name === "modal_app_history") {
    const limit = integer(input.limit, "limit", 20, 100);
    const appId = await resolveApp(env, input.app);
    const { stdout } = await runCli(["app", "history", appId, "--env", env, "--json"]);
    const history = rows(parseJson(stdout)).map(normalizeHistory);
    return envelope(history.slice(0, limit), { environment: env, appId, total: history.length, truncated: history.length > limit, durationMs: Date.now() - started });
  }

  if (name === "modal_app_logs") {
    const since = timeValue(input.since, "since", "1h");
    const until = timeValue(input.until, "until");
    const tail = integer(input.tail, "tail", 100, 500);
    const appId = await resolveApp(env, input.app);
    const args = ["app", "logs", appId, "--env", env, "--since", since, "--tail", String(tail), "--timestamps", "--show-function-id", "--show-function-call-id", "--show-container-id"];
    if (until) args.push("--until", until);
    if (input.source !== undefined) {
      if (!SOURCE_VALUES.has(input.source)) throw new ModalMcpError("INVALID_INPUT", "source is invalid.");
      args.push("--source", input.source);
    }
    const search = optionalString(input.search, "search", undefined, 256);
    if (search) args.push("--search", search);
    const functionId = optionalString(input.functionId, "functionId", ID_PATTERNS.function, 128);
    if (functionId) args.push("--function", functionId);
    const functionCallId = optionalString(input.functionCallId, "functionCallId", ID_PATTERNS.functionCall, 128);
    if (functionCallId) args.push("--function-call", functionCallId);
    const containerId = optionalString(input.containerId, "containerId", ID_PATTERNS.container, 128);
    if (containerId) args.push("--container", containerId);
    const { stdout } = await runCli(args, { maxBuffer: LOG_OUTPUT_LIMIT });
    const logs = redact(stdout);
    if (Buffer.byteLength(logs, "utf8") > LOG_OUTPUT_LIMIT) throw new ModalMcpError("OUTPUT_LIMIT", "Log output exceeded 256 KiB after redaction.");
    return envelope({ logs }, { environment: env, appId, since, until: until || null, tail, bytes: Buffer.byteLength(logs, "utf8"), durationMs: Date.now() - started });
  }

  const limit = integer(input.limit, "limit", 100, 500);
  const args = ["container", "list", "--env", env, "--json"];
  let appId = null;
  if (input.app !== undefined) {
    appId = await resolveApp(env, input.app);
    args.push("--app-id", appId);
  }
  const { stdout } = await runCli(args);
  const containers = rows(parseJson(stdout)).map(normalizeContainer);
  return envelope(containers.slice(0, limit), { environment: env, appId, total: containers.length, truncated: containers.length > limit, durationMs: Date.now() - started });
}

function errorResult(error) {
  const normalized = error instanceof ModalMcpError ? error : new ModalMcpError("CLI_FAILED", redact(error?.message || error));
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify({ ok: false, error: { code: normalized.code, message: normalized.message } }) }],
  };
}

function successResult(result) {
  return { isError: false, content: [{ type: "text", text: JSON.stringify(result) }] };
}

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

async function handle(message) {
  if (!message || message.jsonrpc !== "2.0") return;
  if (message.method === "notifications/initialized") return;
  const id = message.id;
  if (id === undefined) return;

  if (message.method === "initialize") {
    return send({ jsonrpc: "2.0", id, result: { protocolVersion: message.params?.protocolVersion || "2025-06-18", capabilities: { tools: { listChanged: false } }, serverInfo: { name: SERVER_NAME, version: SERVER_VERSION } } });
  }
  if (message.method === "ping") return send({ jsonrpc: "2.0", id, result: {} });
  if (message.method === "tools/list") return send({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
  if (message.method === "tools/call") {
    try {
      const result = await callTool(message.params?.name, message.params?.arguments || {});
      return send({ jsonrpc: "2.0", id, result: successResult(result) });
    } catch (error) {
      return send({ jsonrpc: "2.0", id, result: errorResult(error) });
    }
  }
  return send({ jsonrpc: "2.0", id, error: { code: -32601, message: "Method not found" } });
}

export function startServer() {
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on("line", (line) => {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      return send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
    }
    void handle(message);
  });
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  if (process.argv.includes("--selftest")) {
    process.stdout.write(`${JSON.stringify({ server: SERVER_NAME, version: SERVER_VERSION, tools: TOOLS.map((tool) => tool.name) })}\n`);
  } else {
    startServer();
  }
}
