#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, "..");
const referencesDir = path.join(skillRoot, "references");
const apiIndexPath = path.join(referencesDir, "modal-api-index.md");
const cliIndexPath = path.join(referencesDir, "modal-cli-index.md");

const docsUrl = "https://modal.com/docs/reference";
const localReferencePath = process.env.MODAL_REFERENCE_HTML;
const expectedCounts = {
  apiAndChangelog: 48,
  cli: 24,
};

const reportFlagIndex = process.argv.indexOf("--report");
const reportPath =
  process.env.MODAL_REFERENCE_COVERAGE_REPORT ||
  (reportFlagIndex >= 0 ? process.argv[reportFlagIndex + 1] : "");

async function loadReferenceHtml() {
  if (localReferencePath) {
    return readFile(localReferencePath, "utf8");
  }

  if (typeof fetch !== "function") {
    throw new Error("Global fetch is unavailable. Set MODAL_REFERENCE_HTML to a saved reference.html file.");
  }

  const response = await fetch(docsUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${docsUrl}: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

function extractReferenceLinks(html) {
  const links = new Set();
  const hrefPattern = /href="(\/docs\/(?:reference|sdk\/py\/latest|cli\/latest)\/[^"#]+)(?:#[^"]*)?"/g;
  for (const match of html.matchAll(hrefPattern)) {
    links.add(`https://modal.com${match[1]}`);
  }
  return [...links].sort();
}

function missingLinks(expected, text) {
  return expected.filter((link) => !text.includes(link));
}

function normalizeLink(link) {
  return link.replace(/#[^#]*$/, "");
}

function extractIndexedLinks(text) {
  const links = new Set();
  const pattern = /https:\/\/modal\.com\/docs\/(?:sdk\/py\/(?:latest\/modal\.[A-Za-z0-9_.]+|changelog)|cli\/latest\/[A-Za-z0-9_-]+)/g;
  for (const match of text.matchAll(pattern)) {
    links.add(normalizeLink(match[0]));
  }
  return [...links].sort();
}

function difference(left, right) {
  const rightSet = new Set(right);
  return left.filter((item) => !rightSet.has(item));
}

async function writeReportFile(report) {
  if (!reportPath) return;
  const absolutePath = path.resolve(process.cwd(), reportPath);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, `${JSON.stringify(report, null, 2)}\n`);
}

if (!existsSync(apiIndexPath) || !existsSync(cliIndexPath)) {
  throw new Error("Modal API or CLI index file is missing.");
}

const [html, apiIndex, cliIndex] = await Promise.all([
  loadReferenceHtml(),
  readFile(apiIndexPath, "utf8"),
  readFile(cliIndexPath, "utf8"),
]);

const links = extractReferenceLinks(html);
const apiLinks = links.filter((link) => link.startsWith("https://modal.com/docs/sdk/py/latest/modal."));
const cliLinks = links.filter((link) => link.startsWith("https://modal.com/docs/cli/latest/"));
const changelogLink = "https://modal.com/docs/sdk/py/changelog";
const apiAndChangelogLinks = [...new Set(apiLinks.concat(changelogLink))].sort();
const indexedApiLinks = extractIndexedLinks(apiIndex).filter((link) =>
  link === changelogLink || link.startsWith("https://modal.com/docs/sdk/py/latest/modal.")
);
const indexedCliLinks = extractIndexedLinks(cliIndex).filter((link) =>
  link.startsWith("https://modal.com/docs/cli/latest/")
);

const missingApi = missingLinks(apiAndChangelogLinks, apiIndex);
const missingCli = missingLinks(cliLinks, cliIndex);
const extraApi = difference(indexedApiLinks, apiAndChangelogLinks);
const extraCli = difference(indexedCliLinks, cliLinks);
const countFailures = [];

if (apiAndChangelogLinks.length !== expectedCounts.apiAndChangelog) {
  countFailures.push(
    `Expected ${expectedCounts.apiAndChangelog} API/changelog links, found ${apiAndChangelogLinks.length}.`
  );
}
if (cliLinks.length !== expectedCounts.cli) {
  countFailures.push(`Expected ${expectedCounts.cli} CLI links, found ${cliLinks.length}.`);
}

const report = {
  checkedAt: new Date().toISOString(),
  docsUrl,
  expectedCounts,
  liveCounts: {
    apiAndChangelog: apiAndChangelogLinks.length,
    cli: cliLinks.length,
  },
  indexedCounts: {
    apiAndChangelog: indexedApiLinks.length,
    cli: indexedCliLinks.length,
  },
  changedLinks: {
    missingApi,
    extraApi,
    missingCli,
    extraCli,
  },
  countFailures,
};

if (missingApi.length || missingCli.length || extraApi.length || extraCli.length || countFailures.length) {
  await writeReportFile(report);
  console.error("Modal reference coverage failed.");
  for (const failure of countFailures) console.error(`- ${failure}`);
  if (missingApi.length) {
    console.error("\nMissing API links:");
    for (const link of missingApi) console.error(`- ${link}`);
  }
  if (extraApi.length) {
    console.error("\nExtra API links no longer in Modal reference:");
    for (const link of extraApi) console.error(`- ${link}`);
  }
  if (missingCli.length) {
    console.error("\nMissing CLI links:");
    for (const link of missingCli) console.error(`- ${link}`);
  }
  if (extraCli.length) {
    console.error("\nExtra CLI links no longer in Modal reference:");
    for (const link of extraCli) console.error(`- ${link}`);
  }
  process.exit(1);
}

await writeReportFile(report);
console.log(`Modal reference coverage ok: ${apiAndChangelogLinks.length} API/changelog links, ${cliLinks.length} CLI links.`);
if (reportPath) console.log(`Modal reference coverage report: ${path.resolve(process.cwd(), reportPath)}`);
