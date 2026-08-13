#!/usr/bin/env node
/** Run all Node unit tests under tests/test_*.js except parity (separate npm script). */
const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const testsDir = path.join(root, "tests");
const files = fs
  .readdirSync(testsDir)
  .filter((f) => /^test_.*\.js$/.test(f) && f !== "test_python_node_parity.js")
  .sort();

if (files.length === 0) {
  console.error("No Node tests found");
  process.exit(1);
}

let failed = 0;
for (const f of files) {
  const full = path.join(testsDir, f);
  console.log(`\n=== ${f} ===`);
  const r = spawnSync(process.execPath, [full], { cwd: root, stdio: "inherit" });
  if (r.status !== 0) {
    failed += 1;
    console.error(`${f} failed with code ${r.status}`);
  }
}
if (failed) {
  console.error(`\n${failed}/${files.length} Node test files failed`);
  process.exit(1);
}
console.log(`\nOK: ${files.length} Node test file(s) passed`);
