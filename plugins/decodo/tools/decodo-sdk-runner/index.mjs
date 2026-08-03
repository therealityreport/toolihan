export const AUTH_ENV_KEYS = ["SCRAPER_API_TOKEN", "DECODO_AUTH_TOKEN", "DECODO_API_TOKEN"];

export function getAuthState(env = process.env) {
  const presentKeys = AUTH_ENV_KEYS.filter((key) => Boolean(env[key]));

  if (presentKeys.length === 0) {
    return {
      status: "missing",
      presentKeys: [],
      missingKeys: AUTH_ENV_KEYS,
      details: "set one supported token env var",
    };
  }

  const malformedKeys = presentKeys.filter((key) => String(env[key]).trim().length < 8);

  if (malformedKeys.length > 0) {
    return {
      status: "malformed",
      presentKeys,
      missingKeys: AUTH_ENV_KEYS.filter((key) => !presentKeys.includes(key)),
      details: `${malformedKeys.join(", ")} too short`,
    };
  }

  return {
    status: "present-untested",
    presentKeys,
    missingKeys: AUTH_ENV_KEYS.filter((key) => !presentKeys.includes(key)),
    details: "not tested without --live",
  };
}

export async function checkSdkImport(packageName = "@decodo/sdk-ts") {
  try {
    await import(packageName);
    return {
      status: "present-untested",
      packageName,
      details: "package import succeeded; no request was sent",
    };
  } catch (error) {
    if (error && error.code === "ERR_MODULE_NOT_FOUND") {
      return {
        status: "missing",
        packageName,
        details: "package import failed; install or configure the published Decodo SDK package",
      };
    }

    return {
      status: "malformed",
      packageName,
      details: "package import threw before any request was sent",
    };
  }
}

export function buildSdkSmokePlan({ live, maxRequests, packageName }) {
  return {
    mode: live ? "live" : "dry-run",
    packageName,
    maxRequests,
    requestCeilingEnforced: true,
    sendsNetworkByDefault: false,
  };
}
