#!/usr/bin/env node
/*
 * render-visuals.mjs - render optional diagram/chart source files for a doc.
 *
 * Looks for nested .mmd and .vl.json files under:
 *   <doc>/visuals/
 *   <doc>/assets/visuals/
 *
 * Outputs:
 *   <doc>/assets/generated/<relative-name>.svg
 *
 * Usage:
 *   node render-visuals.mjs <topic-slug | /absolute/doc/dir>
 *   node render-visuals.mjs <topic-slug> --format png
 *   node render-visuals.mjs <topic-slug> --dry-run
 */

import { execFileSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  readdirSync,
  statSync,
  writeFileSync
} from 'node:fs';
import {
  basename,
  extname,
  isAbsolute,
  join,
  relative,
  resolve
} from 'node:path';

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const formatArg = args.find((arg) => arg.startsWith('--format='));
const format = formatArg ? formatArg.split('=')[1] : 'svg';
const target = args.find((arg) => !arg.startsWith('--'));

const die = (message) => {
  console.error('render-visuals: ' + message);
  process.exit(1);
};

if (!target) die('usage: node render-visuals.mjs <topic-slug | doc-dir> [--format=svg|png] [--dry-run]');
if (!['svg', 'png'].includes(format)) die('--format must be svg or png');

const KB_ROOT = process.env.KB_ROOT || join(process.cwd(), 'knowledge-base');
const INFO_DOCS = process.env.KB_INFO_DOCS || join(KB_ROOT, 'info-docs');
const docDir = isAbsolute(target) ? target : join(INFO_DOCS, target.replace(/\/+$/, ''));
if (!existsSync(docDir) || !statSync(docDir).isDirectory()) {
  die('doc folder not found: ' + docDir);
}

const visualRoots = [
  join(docDir, 'visuals'),
  join(docDir, 'assets', 'visuals')
].filter((dir) => existsSync(dir) && statSync(dir).isDirectory());

const walk = (dir) => {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(path));
    else if (entry.isFile()) out.push(path);
  }
  return out;
};

const sources = visualRoots.flatMap((root) => walk(root).map((file) => ({ root, file })))
  .filter(({ file }) => file.endsWith('.mmd') || file.endsWith('.vl.json'));

if (!sources.length) {
  console.log('render-visuals: no .mmd or .vl.json files found under visuals/ or assets/visuals/.');
  process.exit(0);
}

const outDir = join(docDir, 'assets', 'generated');
if (!dryRun) mkdirSync(outDir, { recursive: true });

const outputName = (root, file) => {
  const rel = relative(root, file);
  const stripped = file.endsWith('.vl.json')
    ? rel.slice(0, -'.vl.json'.length)
    : rel.slice(0, -extname(rel).length);
  return stripped.replace(/[^A-Za-z0-9._-]+/g, '-');
};

const run = (cmd, cmdArgs, options = {}) => {
  if (dryRun) {
    console.log('  would run: ' + [cmd, ...cmdArgs.map((a) => JSON.stringify(a))].join(' '));
    return options.encoding === null ? Buffer.from('') : '';
  }
  return execFileSync(cmd, cmdArgs, {
    encoding: options.encoding ?? 'utf8',
    stdio: options.capture ? ['ignore', 'pipe', 'inherit'] : 'inherit',
    env: {
      ...process.env,
      NO_UPDATE_NOTIFIER: '1'
    }
  });
};

const rendered = [];
for (const { root, file } of sources) {
  const name = outputName(root, file);
  const out = join(outDir, `${name}.${format}`);

  if (file.endsWith('.mmd')) {
    console.log(`render-visuals: Mermaid ${relative(docDir, file)} -> ${relative(docDir, out)}`);
    run('npx', ['-y', '@mermaid-js/mermaid-cli@latest', '-i', file, '-o', out]);
    rendered.push(out);
    continue;
  }

  if (file.endsWith('.vl.json')) {
    const bin = format === 'png' ? 'vl2png' : 'vl2svg';
    console.log(`render-visuals: Vega-Lite ${relative(docDir, file)} -> ${relative(docDir, out)}`);
    const data = run('npx', ['-y', '-p', 'vega@latest', '-p', 'vega-lite@latest', bin, file], {
      capture: true,
      encoding: format === 'png' ? null : 'utf8'
    });
    if (!dryRun) writeFileSync(out, data);
    rendered.push(out);
  }
}

console.log(`render-visuals: ${dryRun ? 'planned' : 'rendered'} ${rendered.length} asset(s).`);
for (const file of rendered) console.log('  - ' + file);
