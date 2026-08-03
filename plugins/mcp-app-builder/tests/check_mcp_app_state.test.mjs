import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

const SCRIPT = path.resolve(new URL("../scripts/check_mcp_app_state.mjs", import.meta.url).pathname);

function writeJson(filePath, value) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, JSON.stringify(value, null, 2) + "\n");
}

function fixture() {
  const root = mkdtempSync(path.join(os.tmpdir(), "mcp-app-state-"));
  const cache = path.join(root, "plugins-cache");
  const actions = path.join(root, "actions");
  const source = path.join(root, "source");
  const config = path.join(root, "config.toml");
  const ids = {
    bundled: "asdk_app_bundled",
    hosted: "asdk_app_hosted",
    shared: "connector_shared",
    disabled: "asdk_app_disabled",
    unloaded: "asdk_app_unloaded",
    auth: "asdk_app_auth",
    failed: "asdk_app_failed",
    orphan: "asdk_app_orphan",
    drift: "asdk_app_drift",
  };
  const rows = [
    `[apps.${ids.bundled}]\nenabled = true`,
    `[apps.${ids.hosted}]\nenabled = true`,
    `[apps.${ids.shared}]\nenabled = true`,
    `[apps.${ids.disabled}]\nenabled = false`,
    `[apps.${ids.unloaded}]\nenabled = true`,
    `[apps.${ids.auth}]\nenabled = true`,
    `[apps.${ids.failed}]\nenabled = true`,
    `[apps.${ids.orphan}]\nenabled = true`,
    `[apps.${ids.drift}]\nenabled = true`,
  ];
  writeFileSync(config, rows.join("\n\n") + "\n");

  const addApp = (sourceName, plugin, version, id, app = {}, mcp = false) => {
    const dir = path.join(cache, sourceName, plugin, version);
    writeJson(path.join(dir, ".app.json"), { apps: { [plugin]: { id, ...app } } });
    if (mcp) writeJson(path.join(dir, ".mcp.json"), { mcpServers: { [plugin]: { command: "node" } } });
  };
  addApp("local-plugins", "bundled", "1.0.0", ids.bundled, {}, true);
  addApp("curated", "hosted", "1.0.0", ids.hosted);
  addApp("curated", "shared-one", "1.0.0", ids.shared);
  addApp("curated", "shared-two", "1.0.0", ids.shared);
  addApp("curated", "disabled", "1.0.0", ids.disabled);
  addApp("curated", "unloaded", "1.0.0", ids.unloaded);
  addApp("curated", "auth", "1.0.0", ids.auth, { status: "auth_required" });
  addApp("curated", "failed", "1.0.0", ids.failed, { status: "connection_failed" });
  addApp("curated", "drift", "1.0.0", ids.drift, { version: "cache" });
  addApp("source", "drift", "1.0.0", ids.drift, { version: "source" });

  writeJson(path.join(actions, "actions.json"), {
    tools: [
      {
        connector_id: ids.bundled,
        tool_name: "render",
        tool: { _meta: { link_id: "link-bundled" } },
      },
      {
        connector_id: ids.hosted,
        tool_name: "read",
        tool: { _meta: { link_id: "link-hosted" } },
      },
      {
        connector_id: ids.disabled,
        tool_name: "stale",
        tool: { _meta: { link_id: "link-disabled" } },
      },
      {
        connector_id: ids.drift,
        tool_name: "read",
        tool: { _meta: { link_id: "link-drift" } },
      },
    ],
  });
  writeJson(path.join(source, "drift", ".app.json"), { apps: { drift: { id: ids.drift, version: "source" } } });
  return { root, cache, actions, source, config, ids, actionFile: path.join(actions, "actions.json") };
}

function run(fixtureData, ...flags) {
  const result = spawnSync(process.execPath, [SCRIPT, "--all-installed", "--config", fixtureData.config,
    "--plugin-cache-root", fixtureData.cache, "--codex-app-tools", fixtureData.actions,
    "--source-root", fixtureData.source, "--json", ...flags], { encoding: "utf8" });
  assert.equal(result.error, undefined);
  return { ...result, json: result.stdout ? JSON.parse(result.stdout) : null };
}

test("all-installed doctor classifies states and safely repairs disabled wrappers", () => {
  const data = fixture();
  const check = run(data);
  assert.equal(check.status, 1);
  const statuses = Object.fromEntries(check.json.apps.map((app) => [app.id, app.status]));
  assert.deepEqual(statuses, {
    [data.ids.auth]: "auth_required",
    [data.ids.bundled]: "bundled_mcp_app",
    [data.ids.disabled]: "disabled_but_cached",
    [data.ids.drift]: "source_cache_drift",
    [data.ids.failed]: "connection_failed",
    [data.ids.hosted]: "hosted_app",
    [data.ids.orphan]: "orphan_config",
    [data.ids.shared]: "shared_connector",
    [data.ids.unloaded]: "enabled_not_loaded",
  });

  const dryRun = run(data, "--dry-run");
  assert.equal(dryRun.status, 1);
  assert.equal(dryRun.json.repairs.mode, "dry-run");
  assert.equal(dryRun.json.repairs.wouldChange, true);

  const before = readFileSync(data.actionFile, "utf8");
  const applied = run(data, "--apply");
  assert.equal(applied.status, 1, "other proven fixture issues remain after cleanup");
  assert.equal(applied.json.repairs.changedTools, 1);
  assert.equal(applied.json.repairs.backups.length, 1);
  assert.notEqual(readFileSync(data.actionFile, "utf8"), before);
  assert.equal(JSON.parse(readFileSync(data.actionFile, "utf8")).tools.some((tool) => tool.connector_id === data.ids.disabled), false);

  const secondApply = run(data, "--apply");
  assert.equal(secondApply.json.repairs.changedTools, 0);
  assert.deepEqual(secondApply.json.repairs.backups, []);

  const rollback = execFileSync(process.execPath, [SCRIPT, "--rollback", applied.json.repairs.backups[0], "--json"], { encoding: "utf8" });
  assert.equal(JSON.parse(rollback).rollback.restored, true);
  assert.equal(JSON.parse(readFileSync(data.actionFile, "utf8")).tools.some((tool) => tool.connector_id === data.ids.disabled), true);
});

test("invalid action-cache JSON is reported without leaking its contents", () => {
  const data = fixture();
  writeFileSync(path.join(data.actions, "broken.json"), '{"tools": [');
  const result = run(data);
  assert.equal(result.status, 1);
  assert.deepEqual(result.json.actionCache.malformedFiles, ["broken.json"]);
  assert.equal(JSON.stringify(result.json).includes("tools\": ["), false);
});
