#!/usr/bin/env node

import {
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const LOCAL_ARCHETYPES = new Set(["tool-only", "vanilla-widget", "interactive-decoupled"]);
const TARGETS = new Set(["standalone", "codex-plugin"]);
const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROUTED_ARCHETYPES = {
  "react-widget":
    "Adapt the closest official React or bundled UI example, then run the scaffold validator and TypeScript checks.",
  "submission-ready":
    "Start from an existing scaffold, then add auth, security/privacy review, metadata optimization, test cases, and submission checklist artifacts.",
};

function toSlug(value) {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || "example-mcp-app";
}

function toToolName(value) {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
  return normalized || "show_example";
}

function toTitle(value) {
  const words = value
    .trim()
    .replace(/[_-]+/g, " ")
    .split(/\s+/)
    .filter(Boolean);
  if (words.length === 0) {
    return "Example MCP App";
  }
  return words.map((word) => word[0].toUpperCase() + word.slice(1)).join(" ");
}

function isPluginAppId(value) {
  return /^(?:plugin_)?asdk_app_[a-z0-9]+$/i.test(value);
}

function fillTemplate(template, mapping) {
  let result = template;
  for (const [key, value] of Object.entries(mapping)) {
    result = result.replaceAll(key, value);
  }
  return result;
}

function writeFile(filePath, content) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, content, "utf8");
}

function ensureTargetDir(targetPath, force) {
  if (existsSync(targetPath)) {
    if (!lstatSync(targetPath).isDirectory()) {
      throw new Error("Output path exists and is not a directory: " + targetPath);
    }
    if (readdirSync(targetPath).length > 0 && !force) {
      throw new Error(
        "Refusing to write into non-empty directory: " +
          targetPath +
          "\nRe-run with --force to overwrite generated files."
      );
    }
  }
  mkdirSync(targetPath, { recursive: true });
}

function buildPackageJson(appSlug, archetype, target) {
  const dependencies = {
    "@modelcontextprotocol/sdk": "^1.29.0",
    zod: "^4.4.3",
  };
  if (archetype !== "tool-only") {
    dependencies["@modelcontextprotocol/ext-apps"] = "^1.7.4";
  }

  const scripts = {
    dev: "tsx watch src/server.ts",
    start: target === "codex-plugin" ? "node mcp/server.bundle.mjs" : "tsx src/server.ts",
    check: "tsc --noEmit",
  };
  const devDependencies = {
    "@types/node": "^26.1.1",
    tsx: "^4.23.0",
    typescript: "^7.0.2",
  };
  if (target === "codex-plugin") {
    scripts.build =
      "esbuild src/server.ts --bundle --platform=node --format=esm --outfile=mcp/server.bundle.mjs";
    scripts.prepare = "npm run build";
    devDependencies.esbuild = "^0.28.1";
  }

  return (
    JSON.stringify(
      {
        name: appSlug,
        private: true,
        type: "module",
        scripts,
        dependencies,
        devDependencies,
      },
      null,
      2
    ) + "\n"
  );
}

function buildCodexPluginManifest(appSlug, appTitle, appId) {
  const manifest = {
    name: appSlug,
    version: "0.1.0",
    description: appTitle + " MCP-backed app for Codex.",
    author: { name: "Generated with MCP App Builder" },
    keywords: ["codex", "mcp", "app"],
    mcpServers: "./.mcp.json",
    interface: {
      displayName: appTitle,
      shortDescription: "Use " + appTitle + " inside Codex.",
      longDescription:
        appTitle + " is a ready-to-use Codex plugin with a bundled MCP server and optional app UI.",
      developerName: "Generated with MCP App Builder",
      category: "Developer Tools",
      capabilities: ["Interactive", "Read"],
      defaultPrompt: ["Open " + appTitle, "Use " + appTitle + " for this task"],
    },
  };
  if (appId) {
    manifest.apps = "./.app.json";
  }
  return JSON.stringify(manifest, null, 2) + "\n";
}

function buildMcpJson(appSlug, appTitle) {
  return (
    JSON.stringify(
      {
        mcpServers: {
          [appSlug]: {
            title: appTitle,
            description: appTitle + " tools and interactive UI.",
            command: "node",
            args: ["${CLAUDE_PLUGIN_ROOT}/mcp/server.bundle.mjs", "--stdio"],
          },
        },
      },
      null,
      2
    ) + "\n"
  );
}

function buildAppJson(appSlug, appId) {
  return (
    JSON.stringify(
      {
        apps: {
          [appSlug]: {
            id: appId,
          },
        },
      },
      null,
      2
    ) + "\n"
  );
}

function updateMarketplace(marketplacePath, outputDir, appSlug, force) {
  const root = path.resolve(path.dirname(marketplacePath), "..", "..");
  const sourcePath = "./" + path.relative(root, outputDir).split(path.sep).join("/");
  const payload = existsSync(marketplacePath)
    ? JSON.parse(readFileSync(marketplacePath, "utf8"))
    : {
        name: path.basename(root),
        interface: { displayName: toTitle(path.basename(root)) },
        plugins: [],
      };
  if (!payload || typeof payload !== "object" || !Array.isArray(payload.plugins)) {
    throw new Error("Marketplace must contain a plugins array: " + marketplacePath);
  }
  const entry = {
    name: appSlug,
    source: { source: "local", path: sourcePath },
    policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" },
    category: "Developer Tools",
  };
  const index = payload.plugins.findIndex((item) => item?.name === appSlug);
  if (index >= 0 && !force) {
    throw new Error(
      "Marketplace entry already exists for " + appSlug + ". Re-run with --force to replace it."
    );
  }
  if (index >= 0) {
    payload.plugins[index] = entry;
  } else {
    payload.plugins.push(entry);
  }
  let backup = null;
  if (existsSync(marketplacePath)) {
    backup =
      marketplacePath + ".bak." + new Date().toISOString().replace(/[:.]/g, "-");
    copyFileSync(marketplacePath, backup);
  }
  writeFile(marketplacePath, JSON.stringify(payload, null, 2) + "\n");
  return backup;
}

function buildTsconfig() {
  return `{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["node"],
    "outDir": "dist"
  },
  "include": ["src/**/*.ts"]
}
`;
}

function buildGitignore() {
  return ["node_modules/", "dist/", ".env", "*.log", ".mcp-app/", ""].join("\n");
}

function buildEnvExample(port) {
  return [
    "# Port the MCP server listens on. The connect orchestrator injects this",
    "# automatically; set it manually only when running `npm start` by hand.",
    "PORT=" + port,
    "",
  ].join("\n");
}

function buildReadme(
  appTitle,
  archetype,
  toolName,
  widgetCallToolName,
  port,
  target,
  appId
) {
  const script = (name) => JSON.stringify(path.join(PLUGIN_ROOT, "scripts", name));
  const widgetLine =
    archetype === "tool-only"
      ? "This starter exposes one typed MCP tool and no UI resource."
      : "This starter exposes one widget resource and uses the MCP Apps bridge for host communication.";
  const decoupledLine =
    archetype === "interactive-decoupled"
      ? "\nThe widget calls `" + widgetCallToolName + "` separately so rendering and data refresh stay decoupled.\n"
      : "\n";

  const pluginSection =
    target === "codex-plugin"
      ? `
## Codex Plugin Package

This directory is a ready-to-install Codex plugin. \`npm install\` builds the self-contained MCP server at \`mcp/server.bundle.mjs\`; \`.mcp.json\` launches that bundle over stdio when the plugin is installed.

- Plugin manifest: \`.codex-plugin/plugin.json\`
- MCP launcher: \`.mcp.json\`
- Bundled server: \`mcp/server.bundle.mjs\`
${
  appId
    ? "- App reference: `.app.json` (`" + appId + "`)"
    : "- App reference: omitted because no backend-issued `plugin_asdk_app...` id was supplied"
}

To expose this plugin through a local catalog, pass \`--marketplace /path/to/.agents/plugins/marketplace.json\` when scaffolding, add that marketplace with \`codex plugin marketplace add\`, then install the plugin from Codex.
`
      : "";

  return `# ${appTitle}

Archetype: \`${archetype}\`
Target: \`${target}\`

${widgetLine}${decoupledLine}
## Run

\`\`\`bash
npm install
npm run check
npm start
\`\`\`

The MCP endpoint is available at \`http://localhost:${port}/mcp\` (override the port with the \`PORT\` env var). A JSON readiness probe is served at \`http://localhost:${port}/healthz\`.
${pluginSection}

## Main Tool

- \`${toolName}\`

## Connect to Codex (one command)

\`\`\`bash
node ${script("connect_codex_app.mjs")} up --app . --mode mcp-server
\`\`\`

This starts the server, registers it with Codex (\`codex mcp add\`), and verifies the connection. Tear it down with \`connect_codex_app.mjs down --app .\`.

## Validation

Run the scaffold validator against this directory:

\`\`\`bash
node ${script("validate_app_scaffold.mjs")} .
\`\`\`

Then run the generated project checks:

\`\`\`bash
npm install
npm run check
\`\`\`

For runtime validation, run the connection probe (or point MCP Inspector) at the running server:

\`\`\`bash
node ${script("verify_codex_connection.mjs")} --app . --port ${port}
\`\`\`

For local Codex plugin/config/cache status:

\`\`\`bash
node ${script("check_codex_local_app.mjs")} --plugin /path/to/plugin --id plugin-id
\`\`\`

For existing MCP app metadata, app IDs, MCP entries, tunnels, and action surfaces:

\`\`\`bash
node ${script("check_mcp_app_state.mjs")} --plugin /path/to/plugin --bridges /path/to/tunnels.json
\`\`\`

Use an HTTPS tunnel only when testing through ChatGPT web.
`;
}

const SHARED_HTTP_SERVER = `
const port = Number(process.env.PORT ?? "__PORT__");
const MCP_PATH = "/mcp";

if (process.argv.includes("--stdio")) {
  await createAppServer().connect(new StdioServerTransport());
} else {
  createServer(async (req, res) => {
  if (!req.url) {
    res.writeHead(400).end("Missing URL");
    return;
  }

  const url = new URL(req.url, "http://" + (req.headers.host ?? "localhost"));
  const isMcpRoute = url.pathname === MCP_PATH || url.pathname.startsWith(MCP_PATH + "/");

  if (req.method === "OPTIONS" && isMcpRoute) {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "content-type, mcp-session-id",
      "Access-Control-Expose-Headers": "Mcp-Session-Id",
    });
    res.end();
    return;
  }

  if (req.method === "GET" && url.pathname === "/healthz") {
    res
      .writeHead(200, {
        "content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
      })
      .end(JSON.stringify({ status: "ok", app: "__APP_SLUG__", port, mcpPath: MCP_PATH }));
    return;
  }

  if (req.method === "GET" && url.pathname === "/") {
    res.writeHead(200, { "content-type": "text/plain" }).end("__APP_TITLE__ MCP server");
    return;
  }

  const transportMethods = new Set(["GET", "POST", "DELETE"]);
  if (isMcpRoute && req.method && transportMethods.has(req.method)) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Expose-Headers", "Mcp-Session-Id");

    const server = createAppServer();
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });

    res.on("close", () => {
      transport.close();
      server.close();
    });

    try {
      await server.connect(transport);
      await transport.handleRequest(req, res);
    } catch (error) {
      console.error("Failed to handle MCP request:", error);
      if (!res.headersSent) {
        res.writeHead(500).end("Internal server error");
      }
    }
    return;
  }

  res.writeHead(404).end("Not Found");
  }).listen(port, () => {
    console.log("__APP_TITLE__ MCP server listening on http://localhost:" + port + MCP_PATH);
  });
}
`;

const TOOL_ONLY_SERVER_TEMPLATE = `import { createServer } from "node:http";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

function createAppServer(): McpServer {
  const server = new McpServer({
    name: "__APP_SLUG__",
    version: "0.1.0",
  });

  server.registerTool(
    "__TOOL_NAME__",
    {
      title: "__APP_TITLE__",
      description:
        "Return a typed starter response for the __APP_TITLE__ MCP server.",
      inputSchema: {
        message: z
          .string()
          .optional()
          .describe("Optional message to echo in the structured response."),
      },
      outputSchema: {
        headline: z.string(),
        message: z.string(),
        generatedAt: z.string(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: true,
      },
    },
    async ({ message }) => {
      const structuredContent = {
        headline: "__APP_TITLE__",
        message:
          message?.trim() ||
          "This tool-only starter is ready for ChatGPT or any MCP client.",
        generatedAt: new Date().toISOString(),
      };

      return {
        content: [
          {
            type: "text" as const,
            text: structuredContent.message,
          },
        ],
        structuredContent,
      };
    }
  );

  return server;
}
__HTTP_SERVER__`;

const WIDGET_SERVER_TEMPLATE = `import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");
const WIDGET_URI = "ui://widget/main-v1.html";
const WIDGET_HTML = readFileSync(path.join(ROOT_DIR, "public", "widget.html"), "utf8");

function buildItems() {
  return [
    { id: "one", label: "Bridge initialized", value: 1 },
    { id: "two", label: "Tool result received", value: 2 },
    { id: "three", label: "Widget state rendered", value: 3 },
  ];
}

function createStructuredContent(message?: string) {
  return {
    headline: "__APP_TITLE__",
    message:
      message?.trim() ||
      "This starter uses the MCP Apps bridge first and treats window.openai as optional host context.",
    source: "__TOOL_NAME__",
    themeHint: "Read window.openai.theme in the widget only when the host exposes it.",
    __INTERACTIVE_FIELDS__
  };
}

function createAppServer(): McpServer {
  const server = new McpServer({
    name: "__APP_SLUG__",
    version: "0.1.0",
  });

  registerAppResource(
    server,
    "main-widget",
    WIDGET_URI,
    {},
    async () => ({
      contents: [
        {
          uri: WIDGET_URI,
          mimeType: RESOURCE_MIME_TYPE,
          text: WIDGET_HTML,
          _meta: {
            ui: {
              prefersBorder: false,
              permissions: {},
              csp: {
                connectDomains: [],
                resourceDomains: [],
              },
            },
            "openai/widgetDescription":
              "__APP_TITLE__ starter widget rendered by the MCP server.",
          },
        },
      ],
    })
  );

__DATA_TOOL_BLOCK__
  registerAppTool(
    server,
    "__TOOL_NAME__",
    {
      title: "__APP_TITLE__",
      description:
        "Render the __APP_TITLE__ starter widget and return structured data for the UI.",
      inputSchema: {
        message: z
          .string()
          .optional()
          .describe("Optional message to show inside the widget."),
      },
      outputSchema: {
        headline: z.string(),
        message: z.string(),
        source: z.string(),
        themeHint: z.string(),
        __INTERACTIVE_OUTPUT_SCHEMA__
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: true,
      },
      _meta: {
        ui: { resourceUri: WIDGET_URI },
        "openai/outputTemplate": WIDGET_URI,
        "openai/toolInvocation/invoking": "Loading __APP_TITLE__",
        "openai/toolInvocation/invoked": "__APP_TITLE__ ready",
      },
    },
    async ({ message }) => {
      const structuredContent = createStructuredContent(message);

      return {
        content: [
          {
            type: "text" as const,
            text: "Rendered the __APP_TITLE__ starter widget.",
          },
        ],
        structuredContent,
        _meta: {
          "openai/outputTemplate": WIDGET_URI,
        },
      };
    }
  );

  return server;
}
__HTTP_SERVER__`;

const DATA_TOOL_BLOCK_TEMPLATE = `  server.registerTool(
    "__DATA_TOOL_NAME__",
    {
      title: "__APP_TITLE__ Data",
      description:
        "Return fresh structured data for the __APP_TITLE__ widget without re-rendering the app resource.",
      inputSchema: {
        reason: z.string().optional().describe("Why the widget is refreshing data."),
      },
      outputSchema: {
        items: z.array(
          z.object({
            id: z.string(),
            label: z.string(),
            value: z.number(),
          })
        ),
        updatedAt: z.string(),
        summary: z.string(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: true,
      },
    },
    async ({ reason }) => {
      const structuredContent = {
        items: buildItems(),
        updatedAt: new Date().toISOString(),
        summary:
          reason?.trim() ||
          "Fresh data returned by a decoupled MCP tool call from the widget.",
      };

      return {
        content: [
          {
            type: "text" as const,
            text: structuredContent.summary,
          },
        ],
        structuredContent,
      };
    }
  );

`;

const WIDGET_TEMPLATE = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>__APP_TITLE__</title>
    <style>
      /*
       * Consume host theme tokens (window.openai / MCP Apps host CSS variables)
       * with safe fallbacks, and keep the body transparent so the host frame
       * owns the chrome. This is what makes the widget render cleanly inside
       * Codex.app's themed iframe.
       */
      :root {
        color-scheme: light dark;
        color: var(--color-text-primary, #111827);
        font-family: var(--font-sans, Inter, ui-sans-serif, system-ui, sans-serif);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        padding: 12px;
        background: transparent;
      }

      main {
        display: grid;
        gap: 12px;
        width: 100%;
        max-width: 460px;
        margin: 0 auto;
      }

      h1 {
        margin: 0;
        font-size: 24px;
        line-height: 1.2;
      }

      p {
        margin: 0;
        line-height: 1.5;
      }

      .panel {
        border: 1px solid var(--color-border-primary, #d8dee8);
        border-radius: var(--border-radius-md, 8px);
        padding: 14px;
        background: var(--color-background-secondary, #ffffff);
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      button {
        border: 0;
        border-radius: var(--border-radius-sm, 6px);
        padding: 9px 12px;
        font: inherit;
        font-weight: 650;
        color: var(--color-text-inverse, #ffffff);
        background: var(--color-background-info, #0f766e);
        cursor: pointer;
      }

      button.secondary {
        background: var(--color-text-secondary, #334155);
      }

      ul {
        display: grid;
        gap: 6px;
        margin: 0;
        padding: 0;
        list-style: none;
      }

      li {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid var(--color-border-primary, #e5e7eb);
        padding-top: 6px;
      }

      .meta {
        color: var(--color-text-secondary, #475569);
        font-size: 13px;
      }
    </style>
  </head>
  <body>
    <main>
      <section class="panel">
        <h1 id="headline">__APP_TITLE__</h1>
        <p id="message">Waiting for the first tool result.</p>
      </section>

      <section class="panel">
        <div class="actions">
          <button id="tool-button" type="button">Refresh</button>
          <button id="message-button" class="secondary" type="button">Explain</button>
        </div>
      </section>

      <section class="panel">
        <ul id="items"></ul>
        <p class="meta" id="meta">Initializing MCP Apps bridge.</p>
      </section>
    </main>

    <script type="module">
      const headlineEl = document.querySelector("#headline");
      const messageEl = document.querySelector("#message");
      const itemsEl = document.querySelector("#items");
      const metaEl = document.querySelector("#meta");
      const toolButtonEl = document.querySelector("#tool-button");
      const messageButtonEl = document.querySelector("#message-button");

      let toolOutput = null;
      let rpcId = 0;
      const pendingRequests = new Map();

      const renderItems = (items) => {
        itemsEl.replaceChildren();
        for (const item of items ?? []) {
          const row = document.createElement("li");
          const label = document.createElement("span");
          const value = document.createElement("strong");
          label.textContent = item.label ?? item.id ?? "Item";
          value.textContent = String(item.value ?? "");
          row.append(label, value);
          itemsEl.append(row);
        }
      };

      const render = () => {
        headlineEl.textContent = toolOutput?.headline ?? "__APP_TITLE__";
        messageEl.textContent =
          toolOutput?.message ?? toolOutput?.summary ?? "Waiting for the first tool result.";
        renderItems(toolOutput?.items);
        const theme = window.openai?.theme ?? "not exposed";
        metaEl.textContent =
          "Bridge: ready | Theme: " +
          theme +
          " | Source: " +
          (toolOutput?.source ?? "__WIDGET_CALL_TOOL_NAME__");
      };

      const rpcNotify = (method, params) => {
        window.parent.postMessage({ jsonrpc: "2.0", method, params }, "*");
      };

      const rpcRequest = (method, params) =>
        new Promise((resolve, reject) => {
          const id = ++rpcId;
          pendingRequests.set(id, { resolve, reject });
          window.parent.postMessage({ jsonrpc: "2.0", id, method, params }, "*");
        });

      window.addEventListener(
        "message",
        (event) => {
          if (event.source !== window.parent) {
            return;
          }

          const message = event.data;
          if (!message || message.jsonrpc !== "2.0") {
            return;
          }

          if (typeof message.id === "number") {
            const pending = pendingRequests.get(message.id);
            if (!pending) {
              return;
            }
            pendingRequests.delete(message.id);
            if (message.error) {
              pending.reject(message.error);
              return;
            }
            pending.resolve(message.result);
            return;
          }

          if (message.method === "ui/notifications/tool-result") {
            toolOutput = message.params?.structuredContent ?? toolOutput;
            render();
          }
        },
        { passive: true }
      );

      const initializeBridge = async () => {
        await rpcRequest("ui/initialize", {
          appInfo: { name: "__APP_SLUG__-widget", version: "0.1.0" },
          appCapabilities: {},
          protocolVersion: "2026-01-26",
        });
        rpcNotify("ui/notifications/initialized", {});
      };

      const bridgeReady = initializeBridge();

      toolButtonEl.addEventListener("click", async () => {
        await bridgeReady;
        const response = await rpcRequest("tools/call", {
          name: "__WIDGET_CALL_TOOL_NAME__",
          arguments: {
            message: "Tool call triggered from the widget.",
            reason: "The widget requested a data refresh.",
          },
        });
        toolOutput = response?.structuredContent ?? toolOutput;
        render();
      });

      messageButtonEl.addEventListener("click", async () => {
        await bridgeReady;
        rpcNotify("ui/message", {
          role: "user",
          content: [
            {
              type: "text",
              text: "Explain how the __APP_TITLE__ widget and MCP tools work.",
            },
          ],
        });
      });

      render();
    </script>
  </body>
</html>
`;

function buildToolOnlyServerTs(appSlug, appTitle, toolName, port) {
  return fillTemplate(TOOL_ONLY_SERVER_TEMPLATE, {
    "__APP_SLUG__": appSlug,
    "__APP_TITLE__": appTitle,
    "__TOOL_NAME__": toolName,
    "__HTTP_SERVER__": fillTemplate(SHARED_HTTP_SERVER, {
      "__APP_TITLE__": appTitle,
      "__APP_SLUG__": appSlug,
      "__PORT__": String(port),
    }),
  });
}

function buildWidgetServerTs(appSlug, appTitle, toolName, dataToolName, archetype, port) {
  const isDecoupled = archetype === "interactive-decoupled";
  const interactiveFields = isDecoupled
    ? 'items: buildItems(),\n    updatedAt: new Date().toISOString(),'
    : "";
  const interactiveOutputSchema = isDecoupled
    ? `items: z.array(
          z.object({
            id: z.string(),
            label: z.string(),
            value: z.number(),
          })
        ),
        updatedAt: z.string(),`
    : "";
  const dataToolBlock = isDecoupled
    ? fillTemplate(DATA_TOOL_BLOCK_TEMPLATE, {
        "__APP_TITLE__": appTitle,
        "__DATA_TOOL_NAME__": dataToolName,
      })
    : "";

  return fillTemplate(WIDGET_SERVER_TEMPLATE, {
    "__APP_SLUG__": appSlug,
    "__APP_TITLE__": appTitle,
    "__TOOL_NAME__": toolName,
    "__DATA_TOOL_NAME__": dataToolName,
    "__DATA_TOOL_BLOCK__": dataToolBlock,
    "__INTERACTIVE_FIELDS__": interactiveFields,
    "__INTERACTIVE_OUTPUT_SCHEMA__": interactiveOutputSchema,
    "__HTTP_SERVER__": fillTemplate(SHARED_HTTP_SERVER, {
      "__APP_TITLE__": appTitle,
      "__APP_SLUG__": appSlug,
      "__PORT__": String(port),
    }),
  });
}

function buildWidgetHtml(appSlug, appTitle, widgetCallToolName) {
  return fillTemplate(WIDGET_TEMPLATE, {
    "__APP_SLUG__": appSlug,
    "__APP_TITLE__": appTitle,
    "__WIDGET_CALL_TOOL_NAME__": widgetCallToolName,
  });
}

function usage() {
  return [
    "Generate a minimal Node Apps SDK starter.",
    "",
    "Usage:",
    "  node scripts/scaffold_node_app.mjs --name \"Smoke App\" --out /tmp/smoke-app --archetype vanilla-widget",
    "  node scripts/scaffold_node_app.mjs --name \"Plugin App\" --out ./plugins/plugin-app --target codex-plugin --app-id plugin_asdk_app_...",
    "",
    "Local archetypes:",
    "  tool-only",
    "  vanilla-widget",
    "  interactive-decoupled",
    "",
    "Targets:",
    "  standalone (default)",
    "  codex-plugin",
    "",
    "Routed archetypes:",
    "  react-widget",
    "  submission-ready",
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
    name: "Example MCP App",
    out: null,
    archetype: "vanilla-widget",
    target: "standalone",
    appId: null,
    marketplace: null,
    toolName: null,
    port: 8787,
    force: false,
  };

  const tokens = [...argv];
  while (tokens.length > 0) {
    const token = tokens.shift();

    if (token === "--name") {
      args.name = readValue(tokens, token);
      continue;
    }

    if (token === "--out") {
      args.out = readValue(tokens, token);
      continue;
    }

    if (token === "--archetype") {
      args.archetype = readValue(tokens, token);
      continue;
    }

    if (token === "--target") {
      args.target = readValue(tokens, token);
      continue;
    }

    if (token === "--app-id") {
      args.appId = readValue(tokens, token);
      continue;
    }

    if (token === "--marketplace") {
      args.marketplace = readValue(tokens, token);
      continue;
    }

    if (token === "--tool-name") {
      args.toolName = readValue(tokens, token);
      continue;
    }

    if (token === "--port") {
      const value = Number(readValue(tokens, token));
      if (!Number.isInteger(value) || value <= 0) {
        throw new Error("Expected a positive integer after --port");
      }
      args.port = value;
      continue;
    }

    if (token === "--force") {
      args.force = true;
      continue;
    }

    if (token === "--help" || token === "-h") {
      console.log(usage());
      process.exit(0);
    }

    if (!args.out && !token.startsWith("--")) {
      args.out = token;
      continue;
    }

    throw new Error("Unknown argument: " + token);
  }

  if (!args.out) {
    throw new Error("Missing required --out directory.\n\n" + usage());
  }

  if (ROUTED_ARCHETYPES[args.archetype]) {
    throw new Error(
      "Archetype '" +
        args.archetype +
        "' is intentionally not generated by this script. " +
        ROUTED_ARCHETYPES[args.archetype]
    );
  }

  if (!LOCAL_ARCHETYPES.has(args.archetype)) {
    throw new Error("Unknown archetype '" + args.archetype + "'.\n\n" + usage());
  }

  if (!TARGETS.has(args.target)) {
    throw new Error("Unknown target '" + args.target + "'.\n\n" + usage());
  }

  if ((args.appId || args.marketplace) && args.target !== "codex-plugin") {
    throw new Error("--app-id and --marketplace require --target codex-plugin");
  }

  if (args.appId && !isPluginAppId(args.appId)) {
    throw new Error(
      "--app-id must be a backend-issued plugin_asdk_app_... id (legacy asdk_app_... ids are also accepted)"
    );
  }

  return args;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const appSlug = toSlug(args.name);
  const appTitle = toTitle(args.name);
  const toolName = toToolName(args.toolName || appSlug);
  const dataToolName = toolName + "_data";
  const widgetCallToolName =
    args.archetype === "interactive-decoupled" ? dataToolName : toolName;
  const outputDir = path.resolve(args.out);

  ensureTargetDir(outputDir, args.force);

  const files = new Map([
    [path.join(outputDir, "package.json"), buildPackageJson(appSlug, args.archetype, args.target)],
    [path.join(outputDir, "tsconfig.json"), buildTsconfig()],
    [path.join(outputDir, ".gitignore"), buildGitignore()],
    [path.join(outputDir, ".env.example"), buildEnvExample(args.port)],
    [
      path.join(outputDir, "README.md"),
      buildReadme(
        appTitle,
        args.archetype,
        toolName,
        widgetCallToolName,
        args.port,
        args.target,
        args.appId
      ),
    ],
  ]);

  if (args.target === "codex-plugin") {
    files.set(
      path.join(outputDir, ".codex-plugin", "plugin.json"),
      buildCodexPluginManifest(appSlug, appTitle, args.appId)
    );
    files.set(path.join(outputDir, ".mcp.json"), buildMcpJson(appSlug, appTitle));
    if (args.appId) {
      files.set(path.join(outputDir, ".app.json"), buildAppJson(appSlug, args.appId));
    }
  }

  if (args.archetype === "tool-only") {
    files.set(
      path.join(outputDir, "src", "server.ts"),
      buildToolOnlyServerTs(appSlug, appTitle, toolName, args.port)
    );
  } else {
    files.set(
      path.join(outputDir, "public", "widget.html"),
      buildWidgetHtml(appSlug, appTitle, widgetCallToolName)
    );
    files.set(
      path.join(outputDir, "src", "server.ts"),
      buildWidgetServerTs(
        appSlug,
        appTitle,
        toolName,
        dataToolName,
        args.archetype,
        args.port
      )
    );
  }

  for (const [filePath, content] of files) {
    writeFile(filePath, content);
  }

  const marketplaceBackup = args.marketplace
    ? updateMarketplace(path.resolve(args.marketplace), outputDir, appSlug, args.force)
    : null;

  console.log("Created " + appTitle + " (" + args.target + ") at " + outputDir);
  if (args.target === "codex-plugin") {
    console.log("Run `npm install && npm run check` to build and verify the plugin app.");
  }
  if (marketplaceBackup) {
    console.log("Marketplace backup: " + marketplaceBackup);
  }
  console.log(
    "MCP endpoint (default): http://localhost:" +
      args.port +
      "/mcp  (override with PORT env var)"
  );
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
