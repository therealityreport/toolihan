#!/usr/bin/env node
/*
 * tag-doc.mjs — finalize a doc's tags and refresh the library index.
 *
 * The infographic-doc skill writes a doc's meta.json with the SEMANTIC tags it
 * inferred from the content (kind / subject / platform / topic). This helper
 * then does the deterministic, easy-to-forget parts:
 *
 *   1. Derives BRAND tags from the doc's Use Cases pages — every
 *      `use-cases-<brand>.html` contributes its <brand> tag. Brands are the one
 *      dimension most often missed by hand.
 *   2. Validates every tag against the controlled vocabulary (tags.json) and
 *      warns about unknown ones (they would silently fall back to "subject").
 *   3. Assigns `order` (max existing + 1) if the doc doesn't have one yet.
 *   4. Writes meta.json back and runs build-index.mjs to regenerate index.html.
 *
 * Semantic tag CHOICE stays with the model (it reads the content); this script
 * guarantees the mechanical correctness around it. Zero dependencies.
 *
 * Usage:
 *   node tag-doc.mjs <slug>            # a document folder, e.g. scrapling
 *   node tag-doc.mjs <slug> --dry-run  # print what it would do; write nothing
 *
 * KB_ROOT defaults to ./knowledge-base in the current project.
 * KB_INFO_DOCS remains available as an explicit document-directory override.
 * tags.json and build-index.mjs always live at KB_ROOT.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';

const BRAND_DIM = 'brand';
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const target = args.find((a) => !a.startsWith('--'));

const die = (msg) => { console.error('tag-doc: ' + msg); process.exit(1); };

if (!target) die('usage: node tag-doc.mjs <slug> [--dry-run]');

const KB_ROOT = process.env.KB_ROOT || join(process.cwd(), 'knowledge-base');
const INFO_DOCS = process.env.KB_INFO_DOCS || join(KB_ROOT, 'info-docs');
if (!existsSync(KB_ROOT)) die('knowledge-base root not found at ' + KB_ROOT + ' (set KB_ROOT to override)');
if (!existsSync(INFO_DOCS)) die('info-docs not found at ' + INFO_DOCS + ' (set KB_INFO_DOCS to override)');

const TAGS = join(KB_ROOT, 'tags.json');
if (!existsSync(TAGS)) die('missing tags.json at ' + TAGS);
const vocab = JSON.parse(readFileSync(TAGS, 'utf8'));
const VOCAB = vocab.tags || {};
const isBrand = (t) => VOCAB[t] === BRAND_DIM;

// ---- resolve the folder doc + its required files ----
const bare = target.replace(/\/+$/, '');
if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(bare)) {
  die('target must be one document-folder slug under info-docs (for example: scrapling)');
}
const folder = join(INFO_DOCS, bare);
if (!existsSync(folder) || !statSync(folder).isDirectory()) {
  die(`document folder "${bare}/" not found under ${INFO_DOCS}; loose single-page documents are not supported`);
}
const entryPath = join(folder, 'index.html');
const metaPath = join(folder, 'meta.json');
if (!existsSync(entryPath)) {
  die(`${entryPath} does not exist — every document folder must contain index.html and meta.json.`);
}

if (!existsSync(metaPath)) {
  die(`${metaPath} does not exist — every document folder must contain index.html and meta.json.`);
}
const meta = JSON.parse(readFileSync(metaPath, 'utf8'));
if (meta.file !== undefined) {
  die(`${metaPath} contains a "file" override; every document entry point must be <folder>/index.html`);
}
if (!Array.isArray(meta.tags)) meta.tags = [];

// ---- 1. derive brand tags from Use Cases pages ----
const addedBrands = [];
const files = readdirSync(folder);
const fromSubpages = files
  .map((f) => /^use-cases-(.+)\.html$/.exec(f))
  .filter(Boolean)
  .map((m) => m[1]);
const candidates = [...fromSubpages];
for (const b of candidates) {
  if (!isBrand(b)) {
    console.warn(`tag-doc: warning — use-cases page implies brand "${b}", which is not a brand tag in tags.json (skipped). Add it under "brand" if it's a real project.`);
    continue;
  }
  if (!meta.tags.includes(b)) { meta.tags.push(b); addedBrands.push(b); }
}

// ---- 2. validate against vocabulary ----
const unknown = meta.tags.filter((t) => !(t in VOCAB));

// ---- 3. assign order if missing ----
let assignedOrder = false;
if (typeof meta.order !== 'number') {
  let max = -1;
  for (const entry of readdirSync(INFO_DOCS, { withFileTypes: true })) {
    const mp = entry.isDirectory() ? join(INFO_DOCS, entry.name, 'meta.json') : null;
    if (mp && existsSync(mp)) {
      const o = JSON.parse(readFileSync(mp, 'utf8')).order;
      if (typeof o === 'number' && o > max) max = o;
    }
  }
  meta.order = max + 1;
  assignedOrder = true;
}

// ---- normalize field order for a stable, readable file ----
const ordered = {};
for (const k of ['title', 'desc', 'tags', 'model', 'order', 'status']) {
  if (meta[k] !== undefined) ordered[k] = meta[k];
}
for (const k of Object.keys(meta)) if (!(k in ordered)) ordered[k] = meta[k];
const json = JSON.stringify(ordered, null, 2) + '\n';

// ---- report ----
console.log(`tag-doc: folder doc → ${metaPath.replace(INFO_DOCS + '/', '')}`);
console.log(`  tags: ${ordered.tags.join(', ') || '(none)'}`);
if (addedBrands.length) console.log(`  + brand tags from Use Cases pages: ${addedBrands.join(', ')}`);
if (assignedOrder) console.log(`  + assigned order: ${ordered.order}`);
if (unknown.length) {
  console.warn(`  ! tags not in tags.json (add them under the right dimension): ${unknown.join(', ')}`);
}

if (dryRun) {
  console.log('--- dry run: meta.json would be ---');
  console.log(json.trimEnd());
  console.log('--- (index not regenerated) ---');
  process.exit(0);
}

// ---- 4. write + regenerate ----
const builder = join(KB_ROOT, 'build-index.mjs');
if (!existsSync(builder)) die('missing build-index.mjs at ' + builder);
writeFileSync(metaPath, json);
execFileSync(process.execPath, [builder], { stdio: 'inherit' });
