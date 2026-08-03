import { spawn } from "node:child_process";
import { redact } from "../decodo-fixtures/redaction.mjs";

const COMPONENT_KEYS = [
  "DECODO_PROXY_HOST",
  "DECODO_PROXY_PORT",
  "DECODO_PROXY_USERNAME",
  "DECODO_PROXY_PASSWORD",
];

const VALID_PROXY_PROTOCOLS = new Set(["http:", "https:", "socks4:", "socks5:", "socks5h:"]);

export function getProxyState(env = process.env) {
  const proxyUrl = env.DECODO_PROXY_URL || env.PROXY_URL || "";

  if (proxyUrl) {
    return getProxyUrlState(proxyUrl);
  }

  const missingKeys = COMPONENT_KEYS.filter((key) => !env[key]);
  if (missingKeys.length > 0) {
    return {
      status: "missing",
      missingKeys,
      details: `set DECODO_PROXY_URL or ${COMPONENT_KEYS.join(", ")}`,
    };
  }

  const port = Number(env.DECODO_PROXY_PORT);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    return {
      status: "malformed",
      missingKeys: [],
      details: "DECODO_PROXY_PORT must be 1-65535",
    };
  }

  return {
    status: "present-untested",
    missingKeys: [],
    details: "component credentials found; not tested without --live",
  };
}

export function getProxyUrlState(proxyUrl) {
  try {
    const parsed = new URL(proxyUrl);
    if (!VALID_PROXY_PROTOCOLS.has(parsed.protocol)) {
      return {
        status: "malformed",
        missingKeys: [],
        details: "unsupported proxy protocol",
      };
    }

    if (!parsed.hostname || !parsed.port || !parsed.username || !parsed.password) {
      return {
        status: "malformed",
        missingKeys: [],
        details: "proxy URL must include host, port, username, and password",
      };
    }

    return {
      status: "present-untested",
      missingKeys: [],
      details: "proxy URL found; not tested without --live",
    };
  } catch {
    return {
      status: "malformed",
      missingKeys: [],
      details: "proxy URL could not be parsed",
    };
  }
}

export function buildProxyUrl(env = process.env) {
  const proxyUrl = env.DECODO_PROXY_URL || env.PROXY_URL || "";

  if (proxyUrl) {
    return proxyUrl;
  }

  const protocol = env.DECODO_PROXY_PROTOCOL || "http";
  const host = env.DECODO_PROXY_HOST;
  const port = env.DECODO_PROXY_PORT;
  const username = encodeURIComponent(env.DECODO_PROXY_USERNAME || "");
  const password = encodeURIComponent(env.DECODO_PROXY_PASSWORD || "");

  return `${protocol}://${username}:${password}@${host}:${port}`;
}

export function runCurlProxyProbe({ env = process.env, targetUrl, maxRequests }) {
  const proxyUrl = buildProxyUrl(env);
  const requestCount = Math.max(1, Math.min(maxRequests, 3));
  const checks = [];

  for (let index = 0; index < requestCount; index += 1) {
    checks.push(runOneCurlProbe({ proxyUrl, targetUrl, requestNumber: index + 1 }));
  }

  return Promise.all(checks);
}

function runOneCurlProbe({ proxyUrl, targetUrl, requestNumber }) {
  return new Promise((resolve) => {
    const args = [
      "--silent",
      "--show-error",
      "--fail",
      "--location",
      "--max-time",
      "20",
      "--proxy",
      proxyUrl,
      targetUrl,
    ];

    const child = spawn("curl", args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: process.env,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (error) => {
      resolve({
        requestNumber,
        status: "failed",
        details: redact(error.message),
      });
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve({
          requestNumber,
          status: "tested-ok",
          details: `received ${stdout.length} bytes`,
        });
      } else {
        resolve({
          requestNumber,
          status: "failed",
          details: redact(stderr || `curl exited ${code}`),
        });
      }
    });
  });
}
