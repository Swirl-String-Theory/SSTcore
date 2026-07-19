#!/usr/bin/env node
'use strict';

/** Remove Python/IDE junk that must not enter the npm tarball. */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');

function rmrf(p) {
  if (!fs.existsSync(p)) return;
  fs.rmSync(p, { recursive: true, force: true });
  console.error('[prepack-clean] removed', path.relative(root, p));
}

function walk(dir, fn) {
  if (!fs.existsSync(dir)) return;
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      if (ent.name === 'node_modules' || ent.name === '.git' || ent.name === 'build' || ent.name === 'build_node') {
        continue;
      }
      if (ent.name === '__pycache__' || ent.name.endsWith('.egg-info')) {
        rmrf(full);
        continue;
      }
      walk(full, fn);
    } else if (ent.isFile()) {
      if (/\.(pyc|pyo)$/i.test(ent.name)) {
        fs.unlinkSync(full);
        console.error('[prepack-clean] removed', path.relative(root, full));
      }
    }
  }
}

walk(path.join(root, 'src'));
walk(path.join(root, 'resources'));
walk(path.join(root, 'scripts'));
walk(path.join(root, 'tests'));
rmrf(path.join(root, 'src', 'SSTcore.egg-info'));

console.error('[prepack-clean] done');
