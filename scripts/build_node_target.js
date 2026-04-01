#!/usr/bin/env node

// Conditionally build the CMake Node addon target (sstcore_node) after configure.
// Reads build_node/CMakeCache.txt for HAVE_SSTCORE_NODE=ON (legacy: HAVE_SWIRL_STRING_CORE_NODE).

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.join(__dirname, '..');
const buildDir = path.join(repoRoot, 'build_node');
const cachePath = path.join(buildDir, 'CMakeCache.txt');

if (!fs.existsSync(buildDir) || !fs.existsSync(cachePath)) {
  console.log('[SSTcore] build_node or CMakeCache.txt missing; skipping CMake Node target build');
  process.exit(0);
}

const cache = fs.readFileSync(cachePath, 'utf8');
const hasNodeTarget =
  /HAVE_SSTCORE_NODE:BOOL=ON/.test(cache) || /HAVE_SWIRL_STRING_CORE_NODE:BOOL=ON/.test(cache);

if (!hasNodeTarget) {
  console.log('[SSTcore] CMake Node addon target not enabled; skipping sstcore_node build');
  process.exit(0);
}

console.log('[SSTcore] Building CMake Node addon target sstcore_node...');

const buildArgs = ['--build', 'build_node', '--target', 'sstcore_node'];
if (process.platform === 'win32') {
  buildArgs.push('--config', 'Release');
}

const result = spawnSync('cmake', buildArgs, {
  cwd: repoRoot,
  stdio: 'inherit',
  shell: true,
});

if (result.error) {
  console.error('[SSTcore] Error spawning cmake:', result.error.message);
}

process.exit(result.status ?? 1);
