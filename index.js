// index.js — SSTcore npm entry (native addon sstcore.node, optional WASM fallback)
'use strict';

const fs = require('fs');
const path = require('path');

let pkgVersion = '0.8.19';
try {
    pkgVersion = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8')).version || pkgVersion;
} catch (_) { /* keep default */ }

let nativeModule = null;
let wasmModule = null;
/** Resolved addon object used for listBindings (sync load only). */
let bindingSource = null;
let loadErrors = [];

const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;
const isBrowser = typeof window !== 'undefined' || (typeof self !== 'undefined' && typeof importScripts === 'function');

function tryRequireNative(p) {
    try {
        if (!fs.existsSync(p)) {
            loadErrors.push(`${p} (missing)`);
            return null;
        }
        const m = require(p);
        return m;
    } catch (err) {
        loadErrors.push(`${p} (${err && err.message ? err.message : err})`);
        return null;
    }
}

function nativeCandidates() {
    const plat = process.platform;
    const arch = process.arch;
    return [
        path.join(__dirname, 'prebuilds', `${plat}-${arch}`, 'sstcore.node'),
        path.join(__dirname, 'build', 'Release', 'sstcore.node'),
        path.join(__dirname, 'build_node', 'Release', 'sstcore.node'),
        path.join(__dirname, 'build_node', 'sstcore.node'),
        path.join(__dirname, 'build_node', 'Debug', 'sstcore.node'),
        path.join(__dirname, 'build_node', 'RelWithDebInfo', 'sstcore.node'),
        path.join(__dirname, 'build', 'sstcore.node'),
    ];
}

function loadNativeModule() {
    if (!isNode) {
        return null;
    }
    const candidates = nativeCandidates();
    for (const p of candidates) {
        const m = tryRequireNative(p);
        if (m) {
            nativeModule = m;
            bindingSource = m;
            return m;
        }
    }
    return null;
}

function wasmLooksUsable(mod) {
    if (!mod || typeof mod !== 'object') return false;
    return (
        typeof mod.computeVelocity === 'function' ||
        typeof mod.biotSavartVelocity === 'function' ||
        typeof mod.engineInfo === 'function' ||
        Object.keys(mod).some((k) => typeof mod[k] === 'function' && k !== 'default')
    );
}

function loadWasmModule() {
    if (isBrowser) {
        try {
            const dynamicImport = new Function('specifier', 'return import(specifier)');
            return dynamicImport('./dist/sstcore_wasm.js').then(module => {
                wasmModule = module;
                bindingSource = module;
                return module;
            }).catch(() =>
                dynamicImport('./dist/swirl_string_core_wasm.js').then(module => {
                    wasmModule = module;
                    bindingSource = module;
                    return module;
                }),
            ).catch(err => {
                loadErrors.push(`WASM async: ${err.message}`);
                return null;
            });
        } catch (err) {
            loadErrors.push(`WASM async: ${err.message}`);
            return null;
        }
    } else if (isNode) {
        const paths = [
            path.join(__dirname, 'dist', 'sstcore_wasm.js'),
            path.join(__dirname, 'dist', 'swirl_string_core_wasm.js'),
        ];
        for (const p of paths) {
            try {
                if (!fs.existsSync(p)) {
                    loadErrors.push(`${p} (missing)`);
                    continue;
                }
                const mod = require(p);
                if (!wasmLooksUsable(mod)) {
                    loadErrors.push(`${p} (no usable exports)`);
                    continue;
                }
                wasmModule = mod;
                bindingSource = mod;
                return mod;
            } catch (err) {
                loadErrors.push(`${p} (${err.message})`);
            }
        }
        return null;
    }
    return null;
}

function buildLoadError() {
    const plat = isNode ? process.platform : 'browser';
    const arch = isNode ? process.arch : 'n/a';
    const tried = loadErrors.length ? loadErrors.join('\n  - ') : '(none recorded)';
    return [
        'SSTcore native addon could not be loaded and no usable WASM fallback is available.',
        `platform=${plat} architecture=${arch}`,
        'Tried paths:',
        `  - ${tried}`,
        'Build with: npm run build:node',
        'Or: cmake -S . -B build_node -DSST_BUILD_PYTHON_BINDINGS=OFF -DSST_NUMERIC_PROFILE=deterministic',
        '    cmake --build build_node --target sstcore_node --config Release',
    ].join('\n');
}

let loadedModule = null;
let usedWasm = false;

if (isNode) {
    loadedModule = loadNativeModule();
    if (!loadedModule) {
        loadedModule = loadWasmModule();
        usedWasm = !!loadedModule;
    }
} else if (isBrowser) {
    loadedModule = loadWasmModule();
    usedWasm = !!loadedModule;
}

function listBindings(pattern, includePrivate) {
    const pat = pattern && String(pattern).toLowerCase();
    const incPriv = !!includePrivate;
    const mod =
        bindingSource ||
        nativeModule ||
        wasmModule ||
        (loadedModule && typeof loadedModule.then !== 'function' ? loadedModule : null);
    if (!mod || typeof mod !== 'object') {
        return { functions: [], classes: [], attributes: [], counts: { functions: 0, classes: 0, attributes: 0 } };
    }
    const keys = Object.keys(mod).sort();
    const functions = [];
    const classes = [];
    const attributes = [];
    for (const name of keys) {
        if (!incPriv && name.length && name[0] === '_') continue;
        if (name === 'listBindings') continue;
        if (pat && !name.toLowerCase().includes(pat)) continue;
        const v = mod[name];
        if (typeof v === 'function') {
            if (/^[A-Z]/.test(name) && v.prototype && Object.getOwnPropertyNames(v.prototype).length > 1) {
                classes.push(name);
            } else {
                functions.push(name);
            }
        } else {
            attributes.push(name);
        }
    }
    return {
        functions,
        classes,
        attributes,
        counts: { functions: functions.length, classes: classes.length, attributes: attributes.length },
    };
}

function wrapEngineInfo(nativeInfo) {
    const base = nativeInfo && typeof nativeInfo === 'object' ? Object.assign({}, nativeInfo) : {};
    base.packageVersion = pkgVersion;
    if (!base.engineVersion) base.engineVersion = pkgVersion;
    if (!base.canonVersion) base.canonVersion = '0.8.20';
    if (base.nodeApiVersion == null) base.nodeApiVersion = 1;
    if (!base.numericProfile) base.numericProfile = 'deterministic';
    if (!base.platform && isNode) base.platform = process.platform;
    if (!base.architecture && isNode) base.architecture = process.arch;
    return base;
}

function wrapCapabilities(nativeCaps) {
    const caps = nativeCaps && typeof nativeCaps === 'object' ? Object.assign({}, nativeCaps) : {
        biotSavart: false,
        knotGeometry: false,
        frenetHelicity: false,
        magnusIntegrator: false,
        sstIntegrator: false,
        continuousReach: false,
        wasmFallback: false,
    };
    caps.wasmFallback = !!usedWasm;
    return caps;
}

function attachMeta(exportsObj) {
    exportsObj.version = pkgVersion;
    exportsObj.listBindings = listBindings;

    const nativeEngineInfo = typeof exportsObj.engineInfo === 'function'
        ? (() => { try { return exportsObj.engineInfo(); } catch (_) { return null; } })()
        : null;
    const nativeCaps = typeof exportsObj.getCapabilities === 'function'
        ? (() => { try { return exportsObj.getCapabilities(); } catch (_) { return null; } })()
        : null;

    exportsObj.engineInfo = function engineInfo() {
        return wrapEngineInfo(nativeEngineInfo || {
            engineVersion: exportsObj.engineVersion || pkgVersion,
            canonVersion: exportsObj.canonVersion || '0.8.20',
            nodeApiVersion: exportsObj.nodeApiVersion || 1,
            numericProfile: exportsObj.numericProfile || 'deterministic',
            compiler: 'unknown',
        });
    };

    exportsObj.getCapabilities = function getCapabilities() {
        if (nativeCaps) return wrapCapabilities(nativeCaps);
        return wrapCapabilities({
            biotSavart: typeof exportsObj.computeVelocity === 'function',
            knotGeometry: typeof exportsObj.computeWrithe === 'function' || !!exportsObj.knotAvailable,
            frenetHelicity: typeof exportsObj.rk4Integrate === 'function',
            magnusIntegrator: !!exportsObj.magnusIntegratorAvailable ||
                typeof exportsObj.createMagnusBernoulliIntegrator === 'function',
            sstIntegrator: typeof exportsObj.computeSstMass === 'function',
            continuousReach: false,
            wasmFallback: usedWasm,
        });
    };

    try {
        const { attachResourceHelpers } = require('./lib/resource_helpers');
        attachResourceHelpers(exportsObj, __dirname);
    } catch (err) {
        loadErrors.push(`resource_helpers: ${err && err.message ? err.message : err}`);
    }

    return exportsObj;
}

if (!loadedModule) {
    if (isNode) {
        throw new Error(buildLoadError());
    }
    const exportsObj = {
        version: pkgVersion,
        error: 'No module available. Please build the native addon or WASM module.',
        isAvailable: false,
        isNative: false,
        isWasm: false,
        listBindings,
        engineInfo() {
            return wrapEngineInfo({ engineVersion: pkgVersion, compiler: 'none' });
        },
        getCapabilities() {
            return wrapCapabilities(null);
        },
    };
    module.exports = exportsObj;
} else if (typeof loadedModule.then === 'function') {
    const exportsObj = {
        version: pkgVersion,
        isAvailable: false,
        isNative: false,
        isWasm: false,
        error: 'WASM module is loading asynchronously. Use await or .then() on the module.',
        listBindings,
        engineInfo() {
            return wrapEngineInfo({ engineVersion: pkgVersion, compiler: 'wasm' });
        },
        getCapabilities() {
            return wrapCapabilities({ wasmFallback: true });
        },
    };
    module.exports = exportsObj;
    module.exports.load = loadedModule.then(module => {
        bindingSource = module || null;
        const asyncExports = attachMeta(Object.assign({}, module || {}));
        asyncExports.isAvailable = true;
        asyncExports.isNative = false;
        asyncExports.isWasm = true;
        return asyncExports;
    });
} else {
    const exportsObj = attachMeta(Object.assign({}, loadedModule || {}));
    exportsObj.isAvailable = true;
    exportsObj.isNative = !!nativeModule;
    exportsObj.isWasm = !!wasmModule && !nativeModule;
    module.exports = exportsObj;
}
