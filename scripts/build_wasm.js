#!/usr/bin/env node
// build_wasm.js - Build WASM with Emscripten when available; otherwise ship a CJS stub for dist/.

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..');
const distDir = path.join(rootDir, 'dist');
const buildDir = path.join(rootDir, 'build_wasm');

function readPackageVersion() {
    try {
        const p = path.join(rootDir, 'package.json');
        return JSON.parse(fs.readFileSync(p, 'utf8')).version || '0.0.0';
    } catch (_) {
        return '0.0.0';
    }
}

function writeWasmStub(reason) {
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir, { recursive: true });
    }
    const version = readPackageVersion();
    const note = String(reason).replace(/\r?\n/g, ' ').trim();
    const body = [
        "'use strict';",
        '// Placeholder WASM bundle: ' + note,
        'module.exports = {',
        '  version: ' + JSON.stringify(version) + ',',
        '  isWasm: true,',
        '  isNative: false,',
        '  isAvailable: false,',
        '  listBindings() {',
        '    return {',
        '      functions: [],',
        '      classes: [],',
        '      attributes: [],',
        '      counts: { functions: 0, classes: 0, attributes: 0 },',
        '    };',
        '  },',
        '};',
        '',
    ].join('\n');
    const out = path.join(distDir, 'swirl_string_core_wasm.js');
    fs.writeFileSync(out, body, 'utf8');
    console.warn(`[build:wasm] Wrote stub ${path.relative(rootDir, out)} (${note}).`);
}

function emccOnPath() {
    try {
        execSync('emcc --version', { stdio: 'ignore' });
        return true;
    } catch (_) {
        return false;
    }
}

console.log('Building WASM module with Emscripten...');

if (!emccOnPath()) {
    writeWasmStub('Emscripten (emcc) not found; install emsdk for a real browser build');
    process.exit(0);
}

if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

try {
    execSync('emcmake cmake -DCMAKE_BUILD_TYPE=Release -DSST_BUILD_PYTHON_BINDINGS=OFF ..', {
        cwd: buildDir,
        stdio: 'inherit',
        shell: true,
    });
} catch (err) {
    console.error('WASM CMake configure failed:', err.message);
    writeWasmStub('Emscripten CMake configure failed');
    process.exit(0);
}

const tryTargets = ['swirl_string_core_wasm', 'sstcore_wasm'];
let built = false;
for (const target of tryTargets) {
    try {
        execSync(`cmake --build . --target ${target}`, {
            cwd: buildDir,
            stdio: 'inherit',
            shell: true,
        });
        built = true;
        console.log(`WASM build completed successfully (target ${target}).`);
        break;
    } catch (_) {
        /* try next */
    }
}

if (!built) {
    writeWasmStub('No Emscripten CMake target succeeded (expected until WASM target is wired in CMake)');
    process.exit(0);
}
