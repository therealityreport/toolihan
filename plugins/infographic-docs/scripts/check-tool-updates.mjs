#!/usr/bin/env node
/*
 * check-tool-updates.mjs - lightweight update check for external helper tools.
 *
 * This complements Tool Finder's check-tool-updates workflow with a plugin-local
 * watch list. It does not install or update anything.
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = join(here, '..');
const configPath = process.argv.find((arg) => arg.endsWith('.json')) || join(pluginRoot, 'tool-finder.update-watch.json');
const strict = process.argv.includes('--strict');

const die = (message) => {
  console.error('check-tool-updates: ' + message);
  process.exit(1);
};

const config = JSON.parse(readFileSync(configPath, 'utf8'));
const npmTools = (config.externalTools || []).filter((tool) => tool.provider === 'npm' && tool.package);

if (!npmTools.length) die('no npm externalTools found in ' + configPath);
if (typeof fetch !== 'function') die('Node fetch() is unavailable. Use Node 18 or newer.');

const registryUrl = (pkg) => `https://registry.npmjs.org/${encodeURIComponent(pkg)}`;

let failures = 0;
console.log(`check-tool-updates: ${config.name || 'tool watch'} (${npmTools.length} npm tools)`);

for (const tool of npmTools) {
  try {
    const res = await fetch(registryUrl(tool.package), {
      headers: { accept: 'application/json' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    const latest = body?.['dist-tags']?.latest || '(unknown)';
    const modified = body?.time?.modified || '(unknown modified time)';
    console.log(`- ${tool.package}: latest ${latest}; modified ${modified}; adoption ${tool.adoption || 'reference'}`);
  } catch (error) {
    failures += 1;
    console.warn(`- ${tool.package}: update check failed (${error.message})`);
  }
}

if (failures && strict) process.exit(1);
if (failures) console.warn(`check-tool-updates: ${failures} check(s) failed; no updates were installed.`);
