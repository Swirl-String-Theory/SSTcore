// index.js — SSTcore npm entry (native addon sstcore.node, optional WASM fallback)
'use strict';

const fs = require('fs');
const path = require('path');

let pkgVersion = '0.2.0';
try {
    pkgVersion = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8')).version || pkgVersion;
} catch (_) { /* keep default */ }

let nativeModule = null;
let wasmModule = null;
/** Resolved addon object used for listBindings (sync load only). */
let bindingSource = null;

const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;
const isBrowser = typeof window !== 'undefined' || (typeof self !== 'undefined' && typeof importScripts === 'function');

function tryRequireNative(p) {
    try {
        return require(p);
    } catch (_) {
        return null;
    }
}

function loadNativeModule() {
    if (!isNode) {
        return null;
    }
    const candidates = [
        path.join(__dirname, 'build', 'Release', 'sstcore.node'),
        path.join(__dirname, 'build', 'Release', 'swirl_string_core.node'),
    ];
    for (const p of candidates) {
        const m = tryRequireNative(p);
        if (m) {
            nativeModule = m;
            bindingSource = m;
            return m;
        }
    }
    console.warn('Native addon not found (tried sstcore.node and swirl_string_core.node); falling back to WASM if available');
    return null;
}

function loadWasmModule() {
    if (isBrowser) {
        try {
            const dynamicImport = new Function('specifier', 'return import(specifier)');
            return dynamicImport('./dist/swirl_string_core_wasm.js').then(module => {
                wasmModule = module;
                bindingSource = module;
                return module;
            }).catch(err => {
                console.warn('WASM module not available:', err.message);
                return null;
            });
        } catch (err) {
            console.warn('WASM module not available:', err.message);
            return null;
        }
    } else if (isNode) {
        try {
            wasmModule = require('./dist/swirl_string_core_wasm.js');
            bindingSource = wasmModule;
            return wasmModule;
        } catch (err) {
            console.warn('WASM module not available:', err.message);
            return null;
        }
    }
    return null;
}

let loadedModule = null;

if (isNode) {
    loadedModule = loadNativeModule();
    if (!loadedModule) {
        loadedModule = loadWasmModule();
    }
} else if (isBrowser) {
    loadedModule = loadWasmModule();
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

let exportsObj = {};

if (!loadedModule) {
    exportsObj.version = pkgVersion;
    exportsObj.error = 'No module available. Please build the native addon or WASM module.';
    exportsObj.isAvailable = false;
    exportsObj.isNative = false;
    exportsObj.isWasm = false;
    exportsObj.listBindings = listBindings;
    module.exports = exportsObj;
} else if (typeof loadedModule.then === 'function') {
    exportsObj.version = pkgVersion;
    exportsObj.isAvailable = false;
    exportsObj.isNative = false;
    exportsObj.isWasm = false;
    exportsObj.error = 'WASM module is loading asynchronously. Use await or .then() on the module.';
    exportsObj.listBindings = listBindings;
    module.exports = exportsObj;
    module.exports.load = loadedModule.then(module => {
        bindingSource = module || null;
        const asyncExports = Object.assign({}, module || {});
        asyncExports.version = pkgVersion;
        asyncExports.isAvailable = true;
        asyncExports.isNative = false;
        asyncExports.isWasm = true;
        asyncExports.listBindings = listBindings;
        return asyncExports;
    });
} else {
    Object.assign(exportsObj, loadedModule || {});
    exportsObj.version = pkgVersion;
    exportsObj.isAvailable = true;
    exportsObj.isNative = !!nativeModule;
    exportsObj.isWasm = !!wasmModule;
    exportsObj.listBindings = listBindings;
    module.exports = exportsObj;
}
