#!/usr/bin/env node
// npm install hook: generate embedded knot sources before node-gyp (best effort).
'use strict';

console.log('Running pre-build steps (knot embed)...');

try {
    require('./ensure_knot_embedded.js');
} catch (err) {
    console.warn('Pre-build step failed (CMake may be unavailable):', err.message);
}
