import { printSafe, printSafeError, redact, redactedError } from "./redaction.mjs";

export function parseCommonArgs(argv, options = {}) {
  const {
    defaultDryRun = false,
    defaultMaxRequests = 1,
    hardMaxRequests = 3,
  } = options;

  const parsed = {
    dryRun: defaultDryRun,
    live: false,
    help: false,
    maxRequests: defaultMaxRequests,
    targetUrl: "",
    packageName: "",
    _: [],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--dry-run") {
      parsed.dryRun = true;
      parsed.live = false;
    } else if (arg === "--live") {
      parsed.live = true;
      parsed.dryRun = false;
    } else if (arg === "--max-requests") {
      index += 1;
      parsed.maxRequests = Number(argv[index]);
    } else if (arg.startsWith("--max-requests=")) {
      parsed.maxRequests = Number(arg.slice("--max-requests=".length));
    } else if (arg === "--target-url") {
      index += 1;
      parsed.targetUrl = argv[index] || "";
    } else if (arg.startsWith("--target-url=")) {
      parsed.targetUrl = arg.slice("--target-url=".length);
    } else if (arg === "--package") {
      index += 1;
      parsed.packageName = argv[index] || "";
    } else if (arg.startsWith("--package=")) {
      parsed.packageName = arg.slice("--package=".length);
    } else {
      parsed._.push(arg);
    }
  }

  if (!Number.isInteger(parsed.maxRequests) || parsed.maxRequests < 1) {
    throw new Error("--max-requests must be a positive integer");
  }

  if (parsed.maxRequests > hardMaxRequests) {
    throw new Error(`--max-requests cannot exceed ${hardMaxRequests}`);
  }

  return parsed;
}

export function printHelp({ name, description, usage, options = [], examples = [] }) {
  printSafe(`${name}\n`);
  printSafe(description);
  printSafe("");
  printSafe(`Usage: ${usage}`);

  if (options.length > 0) {
    printSafe("");
    printSafe("Options:");
    for (const option of options) {
      printSafe(`  ${option}`);
    }
  }

  if (examples.length > 0) {
    printSafe("");
    printSafe("Examples:");
    for (const example of examples) {
      printSafe(`  ${example}`);
    }
  }
}
export function requireCredentials(state, { dryRun, label }) {
  if (dryRun) {
    return;
  }

  if (state.status !== "present-untested" && state.status !== "tested-ok") {
    throw new Error(`${label} credentials are required outside --dry-run mode; status=${state.status}`);
  }
}

export function statusLine(name, state) {
  const details = state.details ? ` ${state.details}` : "";
  return `${name}: ${state.status}${details}`;
}

export function summarizeMissing(keys = []) {
  if (keys.length === 0) {
    return "";
  }
  return `missing ${keys.join(", ")}`;
}

export function safeJson(value) {
  return redact(JSON.stringify(value, null, 2));
}

export async function runCli(main) {
  try {
    const code = await main();
    process.exitCode = code || 0;
  } catch (error) {
    printSafeError(`ERROR: ${redactedError(error)}`);
    process.exitCode = 1;
  }
}
