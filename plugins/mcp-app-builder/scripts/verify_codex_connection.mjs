#!/usr/bin/env node

// Runtime connection probe for a generated MCP app. Starts nothing; it assumes
// the server is already listening (the connect orchestrator starts it) and
// asserts that Codex would be able to connect and, for widget archetypes,
// render the UI resource.
//
// It imports the MCP SDK client from the *generated app's* node_modules so this
// plugin needs no dependencies of its own.

import { createRequire } from "node:module";
import { existsSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const WIDGET_MIME = "text/html;profile=mcp-app";

function usage() {
  return [
    "Verify that a running MCP app accepts an MCP connection (and renders a widget).",
    "",
    "Usage:",
    "  node scripts/verify_codex_connection.mjs --app <app-dir> --port <port> [options]",
    "",
    "Options:",
    "  --app <dir>        Generated app directory (must contain node_modules). Required.",
    "  --port <n>         Port the server listens on. Required.",
    "  --host <h>         Host (default: localhost).",
    "  --archetype <a>    tool-only | vanilla-widget | interactive-decoupled (inferred if omitted).",
    "  --tool <name>      Expected primary tool name (asserted present).",
    "  --call             Additionally call the primary tool and assert structuredContent.",
    "  --timeout <ms>     Overall readiness/handshake timeout (default: 15000).",
    "  --json             Emit a structured JSON report only.",
  ].join("\n");
}

function parseArgs(argv) {
  const args = {
    app: null,
    port: null,
    host: "localhost",
    archetype: null,
    tool: null,
    call: false,
    timeout: 15000,
    json: false,
  };
  const tokens = [...argv];
  const takeValue = (flag) => {
    const value = tokens.shift();
    if (value === undefined || value.startsWith("--")) {
      throw new Error("Expected a value after " + flag);
    }
    return value;
  };
  while (tokens.length > 0) {
    const token = tokens.shift();
    switch (token) {
      case "--app":
        args.app = takeValue(token);
        break;
      case "--port":
        args.port = Number(takeValue(token));
        break;
      case "--host":
        args.host = takeValue(token);
        break;
      case "--archetype":
        args.archetype = takeValue(token);
        break;
      case "--tool":
        args.tool = takeValue(token);
        break;
      case "--call":
        args.call = true;
        break;
      case "--timeout":
        args.timeout = Number(takeValue(token));
        break;
      case "--json":
        args.json = true;
        break;
      case "--help":
      case "-h":
        console.log(usage());
        process.exit(0);
        break;
      default:
        throw new Error("Unknown argument: " + token);
    }
  }
  if (!args.app) {
    throw new Error("Missing required --app <dir>.\n\n" + usage());
  }
  if (!Number.isInteger(args.port) || args.port <= 0) {
    throw new Error("Missing or invalid --port <n>.\n\n" + usage());
  }
  return args;
}

function isWidgetArchetype(appDir, archetype) {
  if (archetype) {
    return archetype !== "tool-only";
  }
  return existsSync(path.join(appDir, "public", "widget.html"));
}

async function loadSdk(appDir) {
  const appRequire = createRequire(path.join(path.resolve(appDir), "package.json"));
  let clientPath;
  let transportPath;
  try {
    clientPath = appRequire.resolve("@modelcontextprotocol/sdk/client/index.js");
    transportPath = appRequire.resolve(
      "@modelcontextprotocol/sdk/client/streamableHttp.js"
    );
  } catch (error) {
    throw new Error(
      "Could not resolve @modelcontextprotocol/sdk from " +
        appDir +
        " — run `npm install` in the app first. (" +
        (error instanceof Error ? error.message : String(error)) +
        ")"
    );
  }
  const { Client } = await import(pathToFileURL(clientPath).href);
  const { StreamableHTTPClientTransport } = await import(
    pathToFileURL(transportPath).href
  );
  return { Client, StreamableHTTPClientTransport };
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

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const appDir = path.resolve(args.app);
  const baseUrl = "http://" + args.host + ":" + args.port;
  const mcpUrl = baseUrl + "/mcp";
  const widget = isWidgetArchetype(appDir, args.archetype);
  const checks = [];
  const record = (name, status, detail) => checks.push({ name, status, detail });

  // 1) Readiness.
  const health = await waitForHealth(baseUrl, args.timeout);
  if (!health.ok) {
    record("health", "fail", "server not ready at " + baseUrl + "/healthz: " + health.error);
    return finish(args, checks, false);
  }
  record("health", "pass", health.body ?? "ok");

  // 2) MCP handshake + inspection.
  let client;
  let transport;
  try {
    const { Client, StreamableHTTPClientTransport } = await loadSdk(appDir);
    transport = new StreamableHTTPClientTransport(new URL(mcpUrl));
    client = new Client(
      { name: "codex-verify", version: "0.1.0" },
      { capabilities: {} }
    );
    await client.connect(transport);
    record("initialize", "pass", "handshake ok");
  } catch (error) {
    record("initialize", "fail", error instanceof Error ? error.message : String(error));
    return finish(args, checks, false);
  }

  let ok = true;
  try {
    // tools/list
    const toolList = await client.listTools();
    const toolNames = (toolList.tools ?? []).map((t) => t.name);
    if (toolNames.length === 0) {
      record("tools/list", "fail", "no tools registered");
      ok = false;
    } else if (args.tool && !toolNames.includes(args.tool)) {
      record("tools/list", "fail", "expected tool `" + args.tool + "` not in [" + toolNames.join(", ") + "]");
      ok = false;
    } else {
      record("tools/list", "pass", toolNames);
    }

    if (widget) {
      // resources/list
      const resourceList = await client.listResources();
      const resources = resourceList.resources ?? [];
      const widgetResource =
        resources.find((r) => (r.mimeType ?? "").includes("mcp-app")) ??
        resources.find((r) => (r.mimeType ?? "").startsWith("text/html")) ??
        resources.find((r) => (r.uri ?? "").startsWith("ui://"));
      if (!widgetResource) {
        record("resources/list", "fail", "no text/html;profile=mcp-app resource found");
        ok = false;
      } else {
        record("resources/list", "pass", widgetResource.uri + " (" + (widgetResource.mimeType ?? "?") + ")");

        // resources/read
        const read = await client.readResource({ uri: widgetResource.uri });
        const first = (read.contents ?? [])[0];
        const html = typeof first?.text === "string" ? first.text : "";
        const looksLikeHtml = /<!doctype html|<html/i.test(html);
        if (html.length > 0 && looksLikeHtml) {
          record("resources/read", "pass", "htmlBytes=" + html.length);
        } else {
          record("resources/read", "fail", "widget HTML missing or not HTML (bytes=" + html.length + ")");
          ok = false;
        }
      }
    } else {
      record("resources/list", "skip", "tool-only archetype");
      record("resources/read", "skip", "tool-only archetype");
    }

    // Optional tools/call
    if (args.call) {
      const toolList2 = await client.listTools();
      const callable =
        args.tool ??
        (toolList2.tools ?? [])
          .map((t) => t.name)
          .find((n) => !n.endsWith("_data")) ??
        (toolList2.tools ?? [])[0]?.name;
      if (!callable) {
        record("tools/call", "fail", "no callable tool");
        ok = false;
      } else {
        const result = await client.callTool({ name: callable, arguments: {} });
        const sc = result.structuredContent;
        if (sc && typeof sc === "object" && Object.keys(sc).length > 0) {
          record("tools/call", "pass", callable + " -> structuredContent(" + Object.keys(sc).length + " keys)");
        } else {
          record("tools/call", "fail", callable + " returned no structuredContent");
          ok = false;
        }
      }
    } else {
      record("tools/call", "skip", "pass --call to exercise");
    }
  } catch (error) {
    record("mcp", "fail", error instanceof Error ? error.message : String(error));
    ok = false;
  } finally {
    try {
      await transport?.close();
    } catch {
      // ignore teardown errors
    }
  }

  return finish(args, checks, ok);
}

function finish(args, checks, ok) {
  if (args.json) {
    console.log(JSON.stringify({ ok, checks }, null, 2));
  } else {
    console.log((ok ? "Connection verified" : "Connection verification FAILED") + ":");
    for (const check of checks) {
      const detail =
        check.detail === undefined
          ? ""
          : " — " + (typeof check.detail === "string" ? check.detail : JSON.stringify(check.detail));
      console.log("- " + check.name + ": " + check.status + detail);
    }
  }
  process.exit(ok ? 0 : 1);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
