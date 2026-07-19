#!/usr/bin/env node
'use strict';

/**
 * Fail CI if the npm pack is unreasonably large (source-bloat guard).
 * Usage: node scripts/check_npm_pack_size.js
 *        node scripts/check_npm_pack_size.js --json <pack-dry-run.json>
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '..');
const MAX_UNPACKED_BYTES = 100 * 1024 * 1024; // 100 MB
const MAX_FILES = 1500;

function loadEntry(argv) {
  const jsonFlag = argv.indexOf('--json');
  if (jsonFlag >= 0 && argv[jsonFlag + 1]) {
    const raw = fs.readFileSync(argv[jsonFlag + 1], 'utf8');
    const start = raw.indexOf('[');
    const data = JSON.parse(raw.slice(start >= 0 ? start : 0));
    return Array.isArray(data) ? data[0] : data;
  }
  const r = spawnSync('npm', ['pack', '--dry-run', '--json'], {
    cwd: root,
    encoding: 'utf8',
    shell: true,
  });
  if (r.status !== 0) {
    console.error(r.stdout || '');
    console.error(r.stderr || '');
    process.exit(r.status || 1);
  }
  const out = (r.stdout || '').trim();
  const start = out.indexOf('[');
  const data = JSON.parse(out.slice(start >= 0 ? start : 0));
  return Array.isArray(data) ? data[0] : data;
}

const entry = loadEntry(process.argv.slice(2));
const unpacked = Number(entry.unpackedSize || 0);
const files = Number(entry.entryCount || (entry.files && entry.files.length) || 0);
const filename = entry.filename || entry.name || '(unknown)';

console.log(`[pack-size] filename=${filename}`);
console.log(`[pack-size] unpackedSize=${unpacked} bytes (${(unpacked / (1024 * 1024)).toFixed(1)} MB)`);
console.log(`[pack-size] files=${files}`);
console.log(`[pack-size] limits: unpacked<=${MAX_UNPACKED_BYTES} files<=${MAX_FILES}`);

let failed = false;
if (unpacked > MAX_UNPACKED_BYTES) {
  console.error(`[pack-size] FAIL: unpacked size ${unpacked} > ${MAX_UNPACKED_BYTES}`);
  failed = true;
}
if (files > MAX_FILES) {
  console.error(`[pack-size] FAIL: file count ${files} > ${MAX_FILES}`);
  failed = true;
}
{
  const pkgName = entry.name || '';
  const okName =
    pkgName === 'sst-core' ||
    /^sst-core-/i.test(String(filename)) ||
    String(filename).includes('sst-core');
  if (!okName) {
    console.error(`[pack-size] FAIL: expected package name sst-core (filename=${filename}, name=${pkgName})`);
    failed = true;
  }
}

if (failed) process.exit(1);
console.log('[pack-size] OK');
process.exit(0);
