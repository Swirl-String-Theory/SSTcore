#!/usr/bin/env node
'use strict';

/**
 * Smoke-test the packaged npm tarball in an empty temp directory (Windows-safe).
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '..');

function run(cmd, args, opts = {}) {
  console.log(`[smoke] $ ${cmd} ${args.join(' ')}`);
  const r = spawnSync(cmd, args, {
    stdio: 'inherit',
    shell: true,
    ...opts,
  });
  if (r.error) {
    console.error('[smoke] spawn error:', r.error.message);
    process.exit(1);
  }
  if (r.status !== 0) {
    console.error(`[smoke] command failed with code ${r.status}`);
    process.exit(r.status || 1);
  }
  return r;
}

function runCapture(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, {
    encoding: 'utf8',
    shell: true,
    ...opts,
  });
  if (r.error) {
    console.error('[smoke] spawn error:', r.error.message);
    process.exit(1);
  }
  if (r.status !== 0) {
    console.error(r.stdout || '');
    console.error(r.stderr || '');
    console.error(`[smoke] command failed with code ${r.status}`);
    process.exit(r.status || 1);
  }
  return r;
}

console.log('[smoke] npm pack...');
const pack = runCapture('npm', ['pack', '--json'], { cwd: root });
let tgzName;
try {
  const parsed = JSON.parse(pack.stdout);
  const entry = Array.isArray(parsed) ? parsed[0] : parsed;
  tgzName = entry.filename || entry.name;
} catch (_) {
  // fallback: glob newest sstcore-*.tgz
  const files = fs.readdirSync(root).filter((f) => /^sstcore-.*\.tgz$/i.test(f) || /^SSTcore-.*\.tgz$/i.test(f));
  if (!files.length) {
    console.error('[smoke] could not determine tarball name from npm pack');
    process.exit(1);
  }
  files.sort((a, b) => fs.statSync(path.join(root, b)).mtimeMs - fs.statSync(path.join(root, a)).mtimeMs);
  tgzName = files[0];
}

const tgzPath = path.join(root, tgzName);
if (!fs.existsSync(tgzPath)) {
  console.error('[smoke] tarball missing:', tgzPath);
  process.exit(1);
}
console.log('[smoke] tarball:', tgzPath);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'sstcore-pack-smoke-'));
console.log('[smoke] temp dir:', tmp);

run('npm', ['init', '-y'], { cwd: tmp });
run('npm', ['install', tgzPath], { cwd: tmp });

const probePath = path.join(tmp, 'smoke_probe.js');
fs.writeFileSync(
  probePath,
  [
    "const s = require('sstcore');",
    'const info = s.engineInfo();',
    'console.log(JSON.stringify(info));',
    "if (info.engineVersion !== '0.8.18') process.exit(2);",
    'if (!info.canonVersion) process.exit(3);',
    "if (typeof s.computeVelocity !== 'function') process.exit(4);",
    'const curve = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]];',
    'const grid = [[0.5,0.5,0.5]];',
    's.computeVelocity(curve, grid);',
    "console.log('smoke require+engineInfo+computeVelocity OK');",
  ].join('\n'),
  'utf8',
);
run('node', [probePath], { cwd: tmp });

// npm test from the installed package directory
const pkgRoot = path.join(tmp, 'node_modules', 'SSTcore');
if (!fs.existsSync(pkgRoot)) {
  console.error('[smoke] installed package not found at', pkgRoot);
  process.exit(1);
}
run('npm', ['test'], { cwd: pkgRoot });

console.log('[smoke] packaged tarball smoke OK');
process.exit(0);
