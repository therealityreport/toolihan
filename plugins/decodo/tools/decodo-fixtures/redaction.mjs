const REDACTED = "[REDACTED]";

const SECRET_ENV_KEY_RE =
  /\b((?:SCRAPER|DECODO)_[A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|USERNAME|USER|AUTH|PROXY|URL)|PROXY_(?:URL|USERNAME|PASSWORD|USER|PASS))\s*=\s*([^\s'"`]+|"[^"]*"|'[^']*')/gi;

const JSON_SECRET_RE =
  /(["'](?:scraper|decodo|proxy)?[A-Z0-9_-]*(?:token|key|secret|password|username|auth|proxyUrl|proxy_url)["']\s*:\s*)(["']).*?\2/gi;

const AUTH_HEADER_RE =
  /\b(Authorization\s*:\s*)(Basic|Bearer)\s+[A-Za-z0-9._~+/=-]+/gi;

const DASHBOARD_CREDENTIAL_RE =
  /\b(curl\s+[^"'`\n]*?(?:-H|--header)\s+["']?Authorization\s*:\s*)(Basic|Bearer)\s+[A-Za-z0-9._~+/=-]+/gi;

const PROXY_URL_RE =
  /\b((?:https?|socks5h?|socks4):\/\/)([^:@\s/?#]+):([^@\s/?#]+)@([^ \t\r\n"'`<>]+)/gi;

const USER_PASS_AT_RE = /\b([^:@\s]{3,}):([^:@\s]{3,})@/g;

const NAMED_SECRET_RE =
  /\b((?:token|secret|password|passwd|pwd|username)\s*[:=]\s*)([^\s'"`]+|"[^"]*"|'[^']*')/gi;

export function redact(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value)
    .replace(DASHBOARD_CREDENTIAL_RE, `$1$2 ${REDACTED}`)
    .replace(AUTH_HEADER_RE, `$1$2 ${REDACTED}`)
    .replace(PROXY_URL_RE, `$1${REDACTED}@$4`)
    .replace(USER_PASS_AT_RE, `${REDACTED}@`)
    .replace(SECRET_ENV_KEY_RE, `$1=${REDACTED}`)
    .replace(JSON_SECRET_RE, `$1"$${REDACTED}"`.replace("$[", "["))
    .replace(NAMED_SECRET_RE, `$1${REDACTED}`);
}

export function redactedError(error) {
  if (!error) {
    return "";
  }

  if (typeof error === "string") {
    return redact(error);
  }

  if (process.env.DECODO_DEBUG_STACK === "1") {
    return redact(error.stack || error.message || String(error));
  }

  return redact(error.message || String(error));
}

export function printSafe(message = "") {
  process.stdout.write(`${redact(message)}\n`);
}

export function printSafeError(message = "") {
  process.stderr.write(`${redact(message)}\n`);
}

export function assertNoForbiddenFragments(output, fragments) {
  const leaked = fragments.filter((fragment) => {
    if (!fragment) {
      return false;
    }
    return output.includes(fragment);
  });

  if (leaked.length > 0) {
    throw new Error(`redaction failed for ${leaked.length} forbidden fragment(s)`);
  }
}

export function redactionFixtures() {
  const scraperTokenKey = ["SCRAPER", "API", "TOKEN"].join("_");
  const proxyUser = ["fixture", "proxy", "user"].join("-");
  const proxyPass = ["fixture", "proxy", "pass"].join("-");
  const token = ["fixture", "scraper", "token", "123456789"].join("-");
  const authPair = [proxyUser, proxyPass].join(":");
  const authValue = Buffer.from(authPair).toString("base64");
  const proxyUrl = `http://${authPair}@proxy.example.test:10000`;

  return [
    {
      name: "authorization header",
      raw: `Authorization: Basic ${authValue}`,
      forbidden: [authValue],
    },
    {
      name: "bearer header",
      raw: `Authorization: Bearer ${token}`,
      forbidden: [token],
    },
    {
      name: "env token",
      raw: `${scraperTokenKey}=${token}`,
      forbidden: [token],
    },
    {
      name: "proxy url",
      raw: proxyUrl,
      forbidden: [proxyUser, proxyPass, authPair],
    },
    {
      name: "json password",
      raw: JSON.stringify({ decodoProxyPassword: proxyPass }),
      forbidden: [proxyPass],
    },
    {
      name: "dashboard curl",
      raw: `curl --header "Authorization: Basic ${authValue}" https://api.example.test`,
      forbidden: [authValue],
    },
  ];
}
