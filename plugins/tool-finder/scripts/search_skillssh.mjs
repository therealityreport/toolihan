#!/usr/bin/env node
/**
 * skills.sh provider helper for Tool Finder.
 *
 * Uses Vercel OIDC when available. This script does not store tokens and does
 * not auto-install skills.
 */

const API_BASE = "https://www.skills.sh";

async function getOidcToken() {
  if (process.env.VERCEL_OIDC_TOKEN) {
    return process.env.VERCEL_OIDC_TOKEN;
  }
  try {
    const mod = await import("@vercel/oidc");
    if (typeof mod.getVercelOidcToken === "function") {
      return await mod.getVercelOidcToken();
    }
  } catch {
    return null;
  }
  return null;
}

function usage() {
  console.error("Usage:");
  console.error("  search_skillssh.mjs search <query>");
  console.error("  search_skillssh.mjs curated");
  console.error("  search_skillssh.mjs detail <skill-id>");
  console.error("  search_skillssh.mjs audit <skill-id>");
  process.exit(2);
}

function headersToEvidence(response) {
  return {
    rateLimitRemaining: response.headers.get("X-RateLimit-Remaining"),
    cacheUntil: response.headers.get("Cache-Control"),
    retryAfter: response.headers.get("Retry-After"),
  };
}

function normalizeSkill(skill, apiEvidence = {}) {
  const id = skill.id || skill.slug || skill.name || "unknown";
  const installUrl = skill.installUrl || skill.url || null;
  const providerStatus = {
    provider: "skills.sh",
    variant: null,
    state: "queried",
    searched: true,
    skipped: false,
    requiresAuth: true,
    reason: "skills.sh was queried with Vercel OIDC auth.",
    remediation: [],
    resultCount: null
  };
  return {
    id: `skills.sh:${id}`,
    name: skill.name || id,
    assetType: "skill",
    source: "skills.sh",
    providerSource: "direct-api",
    sourceTrust: skill.curated || skill.sourceType === "well-known" ? "curated" : "unknown",
    ownership: "remote-third-party",
    externalIds: {
      skillsShId: id,
      sourceType: skill.sourceType || null,
      contentHash: skill.hash || null
    },
    location: {
      url: skill.url || null,
      repo: skill.repository || null,
      path: null,
      localPath: null
    },
    capabilities: skill.description ? [skill.description] : [],
    install: {
      status: installUrl ? "installable" : "manual",
      command: installUrl ? `npx skills add ${installUrl}` : null,
      requiresAuth: false,
      installUrl
    },
    safety: {
      status: skill.audit?.status || "unknown",
      riskLevel: skill.audit?.riskLevel || "unknown",
      notes: []
    },
    maintenance: {
      lastUpdated: skill.updatedAt || null,
      isArchived: false,
      installs: skill.installs ?? null,
      isDuplicate: Boolean(skill.isDuplicate),
      signals: []
    },
    apiEvidence,
    providerStatus,
    usageExamples: [],
    alternatives: [],
    score: 0,
    bucket: "reference",
    recommendedAction: installUrl ? "install" : "reference-only",
    reasons: [
      skill.description || "Discovered from skills.sh.",
      skill.curated ? "Curated first-party skill." : "",
      skill.isDuplicate ? "Marked as duplicate by skills.sh." : ""
    ].filter(Boolean),
    penalties: [],
    rejectionReason: null
  };
}

function skippedAuthPayload(command, rest) {
  const query = command === "search" ? rest.join(" ").trim() : null;
  const reason = "No Vercel OIDC token available for skills.sh.";
  const status = {
    provider: "skills.sh",
    variant: command,
    state: "skipped",
    searched: false,
    skipped: true,
    requiresAuth: true,
    reason,
    remediation: [
      "Link a Vercel project that can provide OIDC auth.",
      "Set VERCEL_OIDC_TOKEN for this request."
    ],
    resultCount: 0
  };
  return {
    mode: `skills-sh-${command || "unknown"}-skipped`,
    provider: "skills.sh",
    providerSource: "direct-api",
    query,
    results: [],
    providerStatus: [status],
    skippedProviders: [status],
    notes: [
      reason,
      "Tool Finder continued without skills.sh results.",
      "No skills were installed or modified."
    ]
  };
}

async function request(path, token) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json"
    }
  });
  const apiEvidence = headersToEvidence(response);
  if (response.status === 404 && path.includes("/audit/")) {
    return { status: "unknown", riskLevel: "unknown", apiEvidence, auditMissing: true };
  }
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`skills.sh ${response.status}: ${body}`);
  }
  const data = await response.json();
  return { data, apiEvidence };
}

async function main() {
  const [command, ...rest] = process.argv.slice(2);
  if (!command) usage();

  const token = await getOidcToken();
  if (!token) {
    console.log(JSON.stringify(skippedAuthPayload(command, rest), null, 2));
    return;
  }

  if (command === "search") {
    const query = rest.join(" ").trim();
    if (!query) usage();
    const { data, apiEvidence } = await request(`/api/v1/skills/search?q=${encodeURIComponent(query)}`, token);
    const skills = Array.isArray(data) ? data : data.skills || data.results || [];
    console.log(JSON.stringify({ results: skills.map((skill) => normalizeSkill(skill, { ...apiEvidence, searchType: query.includes(" ") ? "semantic" : "fuzzy" })) }, null, 2));
    return;
  }

  if (command === "curated") {
    const { data, apiEvidence } = await request("/api/v1/skills/curated", token);
    const skills = Array.isArray(data) ? data : data.skills || data.results || [];
    console.log(JSON.stringify({ results: skills.map((skill) => normalizeSkill({ ...skill, curated: true }, { ...apiEvidence, searchType: "curated" })) }, null, 2));
    return;
  }

  if (command === "detail") {
    const id = rest[0];
    if (!id) usage();
    const { data, apiEvidence } = await request(`/api/v1/skills/${encodeURIComponent(id)}`, token);
    console.log(JSON.stringify({ result: normalizeSkill(data, { ...apiEvidence, searchType: "detail" }), raw: data }, null, 2));
    return;
  }

  if (command === "audit") {
    const id = rest[0];
    if (!id) usage();
    const audit = await request(`/api/v1/skills/audit/${encodeURIComponent(id)}`, token);
    console.log(JSON.stringify(audit, null, 2));
    return;
  }

  usage();
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
