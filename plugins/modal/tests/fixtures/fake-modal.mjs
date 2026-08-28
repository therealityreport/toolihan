#!/usr/bin/env node

import fs from "node:fs";

const args = process.argv.slice(2);
const mode = process.env.FAKE_MODAL_MODE || "ok";
if (process.env.FAKE_MODAL_LOG) fs.appendFileSync(process.env.FAKE_MODAL_LOG, `${JSON.stringify(args)}\n`);

if (mode === "hang") {
  setTimeout(() => process.stdout.write("late\n"), 60_000);
} else if (mode === "auth-error") {
  process.stderr.write("Authentication token expired; please log in.\n");
  process.exitCode = 1;
} else if (args.length === 1 && args[0] === "--version") {
  process.stdout.write("modal client version: 9.9.9-test\n");
} else if (args[0] === "profile" && args[1] === "current") {
  process.stdout.write("test-profile\n");
} else if (args[0] === "app" && args[1] === "list") {
  const apps = mode === "ambiguous"
    ? [{ app_id: "ap-one", name: "demo", state: "deployed" }, { app_id: "ap-two", name: "demo", state: "stopped" }]
    : [{ app_id: "ap-one", name: "demo", state: "deployed", created_at: "2026-01-01T00:00:00Z" }, { app_id: "ap-two", name: "other", state: "stopped" }];
  process.stdout.write(`${JSON.stringify(apps)}\n`);
} else if (args[0] === "app" && args[1] === "history") {
  process.stdout.write(`${JSON.stringify([{ version: 3, state: "deployed", created_at: "2026-01-02T00:00:00Z" }, { version: 2, state: "stopped" }])}\n`);
} else if (args[0] === "app" && args[1] === "logs") {
  process.stdout.write("2026-01-02T00:00:00Z fu-one fc-one ta-one token=secret-value\n");
} else if (args[0] === "container" && args[1] === "list") {
  process.stdout.write(`${JSON.stringify([{ container_id: "ta-one", app_id: "ap-one", function_id: "fu-one", state: "running" }])}\n`);
} else {
  process.stderr.write(`unsupported fake command: ${args.join(" ")}\n`);
  process.exitCode = 2;
}
