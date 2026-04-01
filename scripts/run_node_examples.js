#!/usr/bin/env node
// Run every node_examples/*.example.ts with tsx (sequential).
'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const dir = path.join(root, 'node_examples');
if (!fs.existsSync(dir)) {
    console.error('node_examples/ missing');
    process.exit(1);
}

const files = fs.readdirSync(dir).filter((f) => f.endsWith('.example.ts')).sort();
let failed = 0;
for (const f of files) {
    const full = path.join(dir, f);
    console.log(`\n--- ${f} ---`);
    const r = spawnSync(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['tsx', full], {
        stdio: 'inherit',
        cwd: root,
        shell: process.platform === 'win32',
    });
    if (r.status !== 0) {
        failed++;
    }
}
process.exit(failed > 0 ? 1 : 0);
