#!/usr/bin/env node
// Generate build_node/generated/knot_files_embedded.cpp/.h (required by binding.gyp).
'use strict';

const { execFileSync } = require('child_process');
const path = require('path');

const root = path.join(__dirname, '..');
const buildDir = path.join(root, 'build_node');

execFileSync(
    'cmake',
    ['-B', buildDir, '-S', root, '-DSST_BUILD_PYTHON_BINDINGS=OFF'],
    { stdio: 'inherit', cwd: root }
);

const buildArgs = ['--build', buildDir, '--target', 'knot_files_embedded'];
if (process.platform === 'win32') {
    buildArgs.push('--config', 'Release');
}
execFileSync('cmake', buildArgs, { stdio: 'inherit', cwd: root });
