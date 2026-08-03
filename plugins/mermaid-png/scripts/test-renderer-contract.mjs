#!/usr/bin/env node
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const tempDir = await mkdtemp(path.join(os.tmpdir(), "mermaid-png-contract-"));
const input = path.join(tempDir, "diagram.mmd");

function runRenderer(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ["scripts/render-mermaid.mjs", ...args], {
      cwd: pluginRoot,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let output = "";
    child.stdout.on("data", (chunk) => {
      output += chunk;
    });
    child.stderr.on("data", (chunk) => {
      output += chunk;
    });
    child.on("error", reject);
    child.on("close", (code) => resolve({ code, output }));
  });
}

async function expectFailure(args, expectedMessage) {
  const result = await runRenderer(args);
  if (result.code === 0 || !result.output.includes(expectedMessage)) {
    throw new Error(`Expected failure containing "${expectedMessage}", got exit ${result.code}: ${result.output}`);
  }
}

try {
  await writeFile(input, "flowchart LR\n  start --> done\n");
  await expectFailure(
    ["--input", input, "--output", path.join(tempDir, "extensionless"), "--format", "png"],
    "Output path must end in .png or .svg.",
  );
  await expectFailure(
    ["--input", input, "--output", path.join(tempDir, "mismatch.svg"), "--format", "png"],
    "Output extension .svg does not match --format png.",
  );
  console.log("Renderer output-extension contract validated.");
} finally {
  await rm(tempDir, { recursive: true, force: true });
}
