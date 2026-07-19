#!/usr/bin/env node
// Run every examples/example_*.ts with tsx (sequential).
'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const dir = path.join(root, 'examples');
if (!fs.existsSync(dir)) {
    console.error('examples/ missing');
    process.exit(1);
}

const files = fs
    .readdirSync(dir)
    .filter((f) => f.startsWith('example_') && f.endsWith('.ts'))
    .sort();
if (files.length === 0) {
    console.error('No examples/example_*.ts found');
    process.exit(1);
}

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
