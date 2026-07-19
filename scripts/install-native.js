#!/usr/bin/env node
'use strict';

/**
 * SSTcore native installer (CMake-first).
 * 1) Use platform prebuilt if present and loadable
 * 2) Else build via CMake (sstcore_lib + sstcore_node)
 * 3) Verify sstcore.node loads
 * 4) Only allow WASM if a working WASM module exists
 * 5) Exit non-zero if no engine is usable
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '..');
const releaseDir = path.join(root, 'build', 'Release');
const releaseAddon = path.join(releaseDir, 'sstcore.node');
const buildNodeDir = path.join(root, 'build_node');
const numericProfile = process.env.SST_NUMERIC_PROFILE || 'deterministic';

function log(msg) {
  console.log(`[SSTcore install] ${msg}`);
}

function fail(msg, code = 1) {
  console.error(`[SSTcore install] ERROR: ${msg}`);
  process.exit(code);
}

function prebuildPath() {
  const plat = process.platform;
  const arch = process.arch;
  return path.join(root, 'prebuilds', `${plat}-${arch}`, 'sstcore.node');
}

function tryLoadAddon(addonPath) {
  if (!fs.existsSync(addonPath)) return { ok: false, error: 'file missing' };
  try {
    const mod = require(addonPath);
    if (!mod || typeof mod !== 'object') {
      return { ok: false, error: 'module did not export an object' };
    }
    return { ok: true, mod };
  } catch (err) {
    return { ok: false, error: err && err.message ? err.message : String(err) };
  }
}

function copyAddon(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function findBuiltAddon() {
  const candidates = [
    releaseAddon,
    path.join(buildNodeDir, 'Release', 'sstcore.node'),
    path.join(buildNodeDir, 'sstcore.node'),
    path.join(buildNodeDir, 'Debug', 'sstcore.node'),
    path.join(buildNodeDir, 'RelWithDebInfo', 'sstcore.node'),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  // Recursive shallow search under build_node for *.node named sstcore
  if (fs.existsSync(buildNodeDir)) {
    const stack = [buildNodeDir];
    while (stack.length) {
      const dir = stack.pop();
      let entries;
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch (_) {
        continue;
      }
      for (const ent of entries) {
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) {
          if (ent.name === 'CMakeFiles' || ent.name === 'node_modules') continue;
          stack.push(full);
        } else if (ent.isFile() && ent.name === 'sstcore.node') {
          return full;
        }
      }
    }
  }
  return null;
}

function run(cmd, args, opts = {}) {
  log(`$ ${cmd} ${args.join(' ')}`);
  const r = spawnSync(cmd, args, {
    cwd: root,
    stdio: 'inherit',
    shell: process.platform === 'win32',
    env: process.env,
    ...opts,
  });
  if (r.error) {
    fail(`failed to spawn ${cmd}: ${r.error.message}`);
  }
  if (r.status !== 0) {
    fail(`${cmd} exited with code ${r.status}`);
  }
  return r;
}

/** Candidate dirs that may contain node_api.h (GHA hosts often lack install-tree headers). */
function nodeCoreIncludeCandidates() {
  const ver = process.versions.node;
  const execDir = path.dirname(process.execPath);
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const local = process.env.LOCALAPPDATA || '';
  return [
    process.env.NODE_CORE_INCLUDE_DIR,
    path.join(execDir, 'include', 'node'),
    path.join(execDir, '..', 'include', 'node'),
    path.join(local, 'node-gyp', 'Cache', ver, 'include', 'node'),
    path.join(home, '.node-gyp', ver, 'include', 'node'),
    path.join(home, '.cache', 'node-gyp', ver, 'include', 'node'),
    path.join(home, 'Library', 'Caches', 'node-gyp', ver, 'include', 'node'),
  ].filter(Boolean);
}

function findNodeCoreInclude() {
  for (const d of nodeCoreIncludeCandidates()) {
    try {
      if (fs.existsSync(path.join(d, 'node_api.h'))) return path.resolve(d);
    } catch (_) { /* continue */ }
  }
  return null;
}

/**
 * GitHub Actions / setup-node installs do not ship node_api.h next to the binary.
 * Download headers (and Windows node.lib) into the node-gyp cache before CMake.
 */
function ensureNodeHeaders() {
  let dir = findNodeCoreInclude();
  if (dir) {
    log(`Node headers found: ${dir}`);
    return dir;
  }

  log('Node headers (node_api.h) missing; downloading via node-gyp install...');
  const localGyp = path.join(root, 'node_modules', 'node-gyp', 'bin', 'node-gyp.js');
  if (fs.existsSync(localGyp)) {
    run(process.execPath, [localGyp, 'install']);
  } else {
    run('npx', ['--yes', 'node-gyp@10.2.0', 'install']);
  }

  dir = findNodeCoreInclude();
  if (!dir) {
    fail(
      [
        'node_api.h still not found after node-gyp install.',
        'Tried:',
        ...nodeCoreIncludeCandidates().map((d) => `  - ${d}`),
        'Set NODE_CORE_INCLUDE_DIR to a directory containing node_api.h, or run: npx node-gyp install',
      ].join('\n'),
    );
  }
  log(`Node headers ready: ${dir}`);
  return dir;
}

function cmakeHasNodeTarget() {
  const cachePath = path.join(buildNodeDir, 'CMakeCache.txt');
  if (!fs.existsSync(cachePath)) return false;
  const cache = fs.readFileSync(cachePath, 'utf8');
  if (/HAVE_SSTCORE_NODE:BOOL=ON/.test(cache) || /HAVE_SWIRL_STRING_CORE_NODE:BOOL=ON/.test(cache)) {
    return true;
  }
  // Fallback: target project/makefile may exist even if cache flag is stale
  return (
    fs.existsSync(path.join(buildNodeDir, 'sstcore_node.vcxproj')) ||
    fs.existsSync(path.join(buildNodeDir, 'CMakeFiles', 'sstcore_node.dir'))
  );
}

function cmakeConfigureAndBuild() {
  const headerDir = ensureNodeHeaders();
  log(`Building native addon via CMake (profile=${numericProfile})...`);
  const configureArgs = [
    '-S', '.',
    '-B', 'build_node',
    '-DSST_BUILD_PYTHON_BINDINGS=OFF',
    '-DSST_BUILD_CPP_TESTS=OFF',
    '-DSST_COPY_RUNTIME_RESOURCES=OFF',
    `-DSST_NUMERIC_PROFILE=${numericProfile}`,
    `-DNODE_CORE_INCLUDE_DIR=${headerDir}`,
  ];
  run('cmake', configureArgs);

  if (!cmakeHasNodeTarget()) {
    fail(
      [
        'CMake configured but sstcore_node target was not enabled (HAVE_SSTCORE_NODE!=ON).',
        `NODE_CORE_INCLUDE_DIR=${headerDir}`,
        'Check that node-addon-api is installed and node_api.h / node.lib are discoverable.',
        'See build_node/CMakeCache.txt and re-run with a clean build_node/.',
      ].join('\n  '),
    );
  }

  const buildEmbed = ['--build', 'build_node', '--target', 'knot_files_embedded'];
  const buildNode = ['--build', 'build_node', '--target', 'sstcore_node'];
  if (process.platform === 'win32') {
    buildEmbed.push('--config', 'Release');
    buildNode.push('--config', 'Release');
  }
  run('cmake', buildEmbed);
  run('cmake', buildNode);

  const built = findBuiltAddon();
  if (!built) {
    fail('CMake build finished but sstcore.node was not found under build_node/ or build/Release/');
  }
  if (path.resolve(built) !== path.resolve(releaseAddon)) {
    log(`Copying ${built} -> ${releaseAddon}`);
    copyAddon(built, releaseAddon);
  }
}

function wasmLooksUsable() {
  const candidates = [
    path.join(root, 'dist', 'sstcore_wasm.js'),
    path.join(root, 'dist', 'swirl_string_core_wasm.js'),
  ];
  for (const p of candidates) {
    if (!fs.existsSync(p)) continue;
    try {
      const mod = require(p);
      if (mod && typeof mod === 'object') {
        const keys = Object.keys(mod);
        // Reject empty/stub modules with no numerical exports
        const hasUseful =
          typeof mod.computeVelocity === 'function' ||
          typeof mod.biotSavartVelocity === 'function' ||
          typeof mod.engineInfo === 'function' ||
          keys.some((k) => typeof mod[k] === 'function' && k !== 'default');
        if (hasUseful) {
          log(`Usable WASM fallback found at ${p}`);
          return true;
        }
        log(`WASM at ${p} present but has no usable exports; ignoring`);
      }
    } catch (err) {
      log(`WASM at ${p} failed to load: ${err.message}`);
    }
  }
  return false;
}

function installPrebuilt() {
  const pb = prebuildPath();
  log(`Checking prebuilt: ${pb}`);
  const loaded = tryLoadAddon(pb);
  if (!loaded.ok) {
    log(`Prebuilt not usable: ${loaded.error}`);
    return false;
  }
  log('Prebuilt addon loads successfully; installing into build/Release');
  copyAddon(pb, releaseAddon);
  return true;
}

function main() {
  log(`platform=${process.platform} arch=${process.arch} node=${process.version}`);

  if (installPrebuilt()) {
    const v = tryLoadAddon(releaseAddon);
    if (!v.ok) fail(`prebuilt copy could not be loaded from ${releaseAddon}: ${v.error}`);
    log('Native prebuilt install OK');
    process.exit(0);
  }

  // Prefer an already-built addon in this tree (e.g. developer build)
  const existing = findBuiltAddon();
  if (existing) {
    const loaded = tryLoadAddon(existing);
    if (loaded.ok) {
      if (path.resolve(existing) !== path.resolve(releaseAddon)) {
        copyAddon(existing, releaseAddon);
      }
      log(`Using existing native addon at ${existing}`);
      process.exit(0);
    }
    log(`Existing addon at ${existing} failed to load: ${loaded.error}`);
  }

  try {
    cmakeConfigureAndBuild();
  } catch (err) {
    // run()/fail already exits; this is defensive
    fail(err && err.message ? err.message : String(err));
  }

  const verify = tryLoadAddon(releaseAddon);
  if (verify.ok) {
    log('Native CMake install OK (sstcore.node loads)');
    process.exit(0);
  }

  log(`Native addon verify failed: ${verify.error}`);

  if (wasmLooksUsable()) {
    log('Native build/load failed; continuing with verified WASM fallback');
    // Marker so index.js can see WASM was accepted at install time
    fs.mkdirSync(path.join(root, 'dist'), { recursive: true });
    fs.writeFileSync(
      path.join(root, 'dist', '.wasm_fallback_ok'),
      `wasm-ok ${new Date().toISOString()}\n`,
      'utf8',
    );
    process.exit(0);
  }

  fail(
    [
      'No usable SSTcore engine after install.',
      `Tried prebuilt: ${prebuildPath()}`,
      `Tried local: ${releaseAddon}`,
      'Tried CMake build of sstcore_node linked against sstcore_lib.',
      'No working WASM fallback with numerical exports.',
      'Build hint: cmake -S . -B build_node -DSST_BUILD_PYTHON_BINDINGS=OFF -DSST_BUILD_CPP_TESTS=OFF -DSST_COPY_RUNTIME_RESOURCES=OFF -DSST_NUMERIC_PROFILE=deterministic',
      'Then: cmake --build build_node --target sstcore_node --config Release',
      'Or: npm run build:node',
    ].join('\n  '),
  );
}

main();
