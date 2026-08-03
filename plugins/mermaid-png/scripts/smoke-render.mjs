#!/usr/bin/env node
import { mkdtemp, readdir, readFile, rm, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixturesDir = path.join(pluginRoot, "examples", "11.16");
const outputDir = await mkdtemp(path.join(os.tmpdir(), "mermaid-png-smoke-"));

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd: pluginRoot, stdio: ["ignore", "pipe", "pipe"] });
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`${args.join(" ")} failed (${code}): ${stderr.trim()}`));
    });
  });
}

async function verifyPng(file) {
  const [fileStat, header] = await Promise.all([stat(file), readFile(file)]);
  const pngMagic = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (fileStat.size === 0 || header.length < 24 || !header.subarray(0, 8).equals(pngMagic)) {
    throw new Error(`Invalid PNG: ${file}`);
  }

  const width = header.readUInt32BE(16);
  const height = header.readUInt32BE(20);
  if (width === 0 || height === 0) {
    throw new Error(`PNG has invalid dimensions (${width}x${height}): ${file}`);
  }
}

async function verifySvg(file) {
  const [fileStat, text] = await Promise.all([stat(file), readFile(file, "utf8")]);
  const svgRoot = /^(?:(?:<\?xml[\s\S]*?\?>|<!--[\s\S]*?-->|<!DOCTYPE[\s\S]*?>)\s*)*<svg\b[^>]*>/i;
  if (fileStat.size === 0 || !svgRoot.test(text.trimStart())) {
    throw new Error(`Invalid SVG: ${file}`);
  }
}

try {
  const fixtures = (await readdir(fixturesDir)).filter((entry) => entry.endsWith(".mmd")).sort();
  async function renderFixture(fixture) {
    const input = path.join(fixturesDir, fixture);
    for (const format of ["png", "svg"]) {
      console.log(`Rendering ${fixture} as ${format}.`);
      const output = path.join(outputDir, `${path.basename(fixture, ".mmd")}.${format}`);
      await run(process.execPath, ["scripts/render-mermaid.mjs", "--input", input, "--output", output, "--format", format]);
      await (format === "png" ? verifyPng(output) : verifySvg(output));
    }
  }

  for (let index = 0; index < fixtures.length; index += 2) {
    await Promise.all(fixtures.slice(index, index + 2).map(renderFixture));
  }
  console.log(`Rendered and validated ${fixtures.length} Mermaid 11.16 fixtures as PNG and SVG.`);
} finally {
  await rm(outputDir, { recursive: true, force: true });
}
