#!/usr/bin/env node
import { access, mkdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const usage = [
  "Usage:",
  "  node scripts/render-mermaid.mjs --input <diagram.mmd> --output <diagram.png|diagram.svg> [--format png|svg] [--theme default] [--background white] [--width 1600]",
].join("\n");

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const allowedFormats = new Set(["png", "svg"]);

function parseArgs(argv) {
  const options = {
    theme: "default",
    background: "white",
    width: "1600",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }

    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected positional argument: ${arg}`);
    }

    const key = arg.slice(2);
    if (!["input", "output", "format", "theme", "background", "width"].includes(key)) {
      throw new Error(`Unknown option: ${arg}`);
    }

    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${arg}`);
    }

    options[key] = value;
    index += 1;
  }

  return options;
}

async function assertReadableFile(filePath, label) {
  let fileStat;
  try {
    fileStat = await stat(filePath);
  } catch {
    throw new Error(`${label} does not exist: ${filePath}`);
  }

  if (!fileStat.isFile()) {
    throw new Error(`${label} is not a file: ${filePath}`);
  }

  try {
    await access(filePath);
  } catch {
    throw new Error(`${label} is not readable: ${filePath}`);
  }
}

function inferFormat(outputPath, explicitFormat) {
  const extension = path.extname(outputPath).toLowerCase().slice(1);
  if (!allowedFormats.has(extension)) {
    throw new Error("Output path must end in .png or .svg.");
  }

  if (explicitFormat) {
    const normalized = explicitFormat.toLowerCase();
    if (!allowedFormats.has(normalized)) {
      throw new Error(`Unsupported format "${explicitFormat}". Use png or svg.`);
    }
    if (extension !== normalized) {
      throw new Error(`Output extension .${extension} does not match --format ${normalized}.`);
    }
    return normalized;
  }

  return extension;
}

async function resolveMmdc() {
  const binary = process.platform === "win32" ? "mmdc.cmd" : "mmdc";
  const localMmdc = path.join(pluginRoot, "node_modules", ".bin", binary);

  try {
    await access(localMmdc);
    return localMmdc;
  } catch {
    throw new Error(
      `Mermaid CLI is not installed at ${localMmdc}. Run "npm install" from ${pluginRoot} before rendering.`,
    );
  }
}

async function resolvePuppeteerExecutablePath() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  if (process.platform !== "darwin") {
    return undefined;
  }

  const macosChrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  try {
    await access(macosChrome);
    return macosChrome;
  } catch {
    return undefined;
  }
}

function runMmdc(command, args, puppeteerExecutablePath) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: pluginRoot,
      env: {
        ...process.env,
        ...(puppeteerExecutablePath ? { PUPPETEER_EXECUTABLE_PATH: puppeteerExecutablePath } : {}),
      },
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }

      const detail = [stderr.trim(), stdout.trim()].filter(Boolean).join("\n");
      reject(new Error(`Mermaid CLI failed with exit code ${code}${detail ? `:\n${detail}` : "."}`));
    });
  });
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(usage);
    return;
  }

  if (!options.input) {
    throw new Error("Missing required --input path.");
  }
  if (!options.output) {
    throw new Error("Missing required --output path.");
  }

  const inputPath = path.resolve(process.cwd(), options.input);
  const outputPath = path.resolve(process.cwd(), options.output);
  const format = inferFormat(outputPath, options.format);

  const width = Number.parseInt(options.width, 10);
  if (!Number.isInteger(width) || width <= 0) {
    throw new Error("--width must be a positive integer.");
  }

  await assertReadableFile(inputPath, "Input");
  await mkdir(path.dirname(outputPath), { recursive: true });

  const mmdc = await resolveMmdc();
  const puppeteerExecutablePath = await resolvePuppeteerExecutablePath();
  await runMmdc(mmdc, [
    "--input",
    inputPath,
    "--output",
    outputPath,
    "--outputFormat",
    format,
    "--theme",
    options.theme,
    "--backgroundColor",
    options.background,
    "--width",
    String(width),
  ], puppeteerExecutablePath);

  await assertReadableFile(outputPath, "Output");
  console.log(outputPath);
}

main().catch((error) => {
  console.error(error.message);
  console.error(usage);
  process.exit(1);
});
