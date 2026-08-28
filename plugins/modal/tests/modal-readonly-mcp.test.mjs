import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import readline from "node:readline";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { assertAllowedCommand, callTool, TOOLS } from "../scripts/modal-readonly-mcp.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const server = path.join(root, "scripts", "modal-readonly-mcp.mjs");
const fakeCli = path.join(root, "tests", "fixtures", "fake-modal.mjs");

function fakeEnvironment(extra = {}) {
  return { ...process.env, MODAL_CLI: fakeCli, ...extra };
}

function rpcClient(extraEnv = {}) {
  const child = spawn(process.execPath, [server], { env: fakeEnvironment(extraEnv), stdio: ["pipe", "pipe", "pipe"] });
  const rl = readline.createInterface({ input: child.stdout, crlfDelay: Infinity });
  const pending = new Map();
  let nextId = 1;
  rl.on("line", (line) => {
    const message = JSON.parse(line);
    const waiter = pending.get(message.id);
    if (waiter) { pending.delete(message.id); waiter.resolve(message); }
  });
  function request(method, params = {}) {
    const id = nextId++;
    child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { pending.delete(id); reject(new Error(`RPC timeout for ${method}`)); }, 3_000);
      pending.set(id, { resolve: (value) => { clearTimeout(timer); resolve(value); } });
    });
  }
  return { child, request, close: () => { child.stdin.end(); child.kill(); } };
}

function resultBody(response) {
  return JSON.parse(response.result.content[0].text);
}

test("selftest exposes exactly the five frozen tools without invoking Modal", () => {
  const result = spawnSync(process.execPath, [server, "--selftest"], { encoding: "utf8", env: { PATH: process.env.PATH } });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout).tools, ["modal_identity", "modal_apps_list", "modal_app_history", "modal_app_logs", "modal_containers_list"]);
});

test("MCP lifecycle and all five fake-CLI tools work", async (t) => {
  const log = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "modal-mcp-test-")), "calls.jsonl");
  const client = rpcClient({ FAKE_MODAL_LOG: log });
  t.after(() => client.close());

  const initialized = await client.request("initialize", { protocolVersion: "2025-06-18" });
  assert.equal(initialized.result.serverInfo.name, "modal-readonly");
  const listed = await client.request("tools/list");
  assert.deepEqual(listed.result.tools.map((tool) => tool.name), TOOLS.map((tool) => tool.name));

  const identity = resultBody(await client.request("tools/call", { name: "modal_identity", arguments: {} }));
  assert.equal(identity.data.activeProfile, "test-profile");
  assert.equal(identity.data.clientVersion, "9.9.9-test");

  const apps = resultBody(await client.request("tools/call", { name: "modal_apps_list", arguments: { environment: "main" } }));
  assert.equal(apps.data[0].appId, "ap-one");
  const history = resultBody(await client.request("tools/call", { name: "modal_app_history", arguments: { environment: "main", app: "demo" } }));
  assert.equal(history.meta.appId, "ap-one");
  const logs = resultBody(await client.request("tools/call", { name: "modal_app_logs", arguments: { environment: "main", app: "ap-one", tail: 10 } }));
  assert.match(logs.data.logs, /\[REDACTED\]/);
  assert.doesNotMatch(logs.data.logs, /secret-value/);
  const containers = resultBody(await client.request("tools/call", { name: "modal_containers_list", arguments: { environment: "main", app: "ap-one" } }));
  assert.equal(containers.data[0].containerId, "ta-one");

  const calls = fs.readFileSync(log, "utf8").trim().split("\n").map(JSON.parse);
  assert.equal(calls.some((args) => args.includes("--follow") || args.includes("-f")), false);
  assert.equal(calls.some((args) => args.some((arg) => ["deploy", "rollback", "rollover", "stop", "exec", "token", "setup", "activate"].includes(arg))), false);
});

test("ambiguous app names fail closed", async () => {
  const previous = { cli: process.env.MODAL_CLI, mode: process.env.FAKE_MODAL_MODE };
  process.env.MODAL_CLI = fakeCli;
  process.env.FAKE_MODAL_MODE = "ambiguous";
  try {
    await assert.rejects(() => callTool("modal_app_history", { environment: "main", app: "demo" }), (error) => error.code === "AMBIGUOUS_APP");
  } finally {
    if (previous.cli === undefined) delete process.env.MODAL_CLI; else process.env.MODAL_CLI = previous.cli;
    if (previous.mode === undefined) delete process.env.FAKE_MODAL_MODE; else process.env.FAKE_MODAL_MODE = previous.mode;
  }
});

test("authentication errors are returned once without retry or repair", async (t) => {
  const log = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "modal-mcp-auth-")), "calls.jsonl");
  const client = rpcClient({ FAKE_MODAL_MODE: "auth-error", FAKE_MODAL_LOG: log });
  t.after(() => client.close());
  await client.request("initialize", { protocolVersion: "2025-06-18" });
  const response = await client.request("tools/call", { name: "modal_apps_list", arguments: { environment: "main" } });
  assert.equal(response.result.isError, true);
  assert.equal(resultBody(response).error.code, "AUTH_REQUIRED");
  const calls = fs.readFileSync(log, "utf8").trim().split("\n").filter(Boolean).map(JSON.parse);
  assert.equal(calls.length, 1);
  assert.deepEqual(calls[0].slice(0, 2), ["app", "list"]);
});

test("timeouts and input bounds fail without retry", async () => {
  const previous = { cli: process.env.MODAL_CLI, mode: process.env.FAKE_MODAL_MODE, timeout: process.env.MODAL_MCP_TIMEOUT_MS };
  process.env.MODAL_CLI = fakeCli;
  process.env.FAKE_MODAL_MODE = "hang";
  process.env.MODAL_MCP_TIMEOUT_MS = "50";
  try {
    await assert.rejects(() => callTool("modal_apps_list", { environment: "main" }), (error) => error.code === "TIMEOUT");
    await assert.rejects(() => callTool("modal_app_logs", { environment: "main", app: "ap-one", tail: 501 }), (error) => error.code === "INVALID_INPUT");
  } finally {
    for (const [key, value] of [["MODAL_CLI", previous.cli], ["FAKE_MODAL_MODE", previous.mode], ["MODAL_MCP_TIMEOUT_MS", previous.timeout]]) {
      if (value === undefined) delete process.env[key]; else process.env[key] = value;
    }
  }
});

test("the command allowlist structurally rejects mutation and authentication verbs", () => {
  for (const args of [
    ["deploy", "app.py"],
    ["app", "rollback", "ap-one"],
    ["app", "stop", "ap-one"],
    ["container", "exec", "ta-one", "sh"],
    ["token", "new"],
    ["profile", "activate", "other"],
    ["setup"],
  ]) assert.throws(() => assertAllowedCommand(args), /allowlist|forbidden/);
});
