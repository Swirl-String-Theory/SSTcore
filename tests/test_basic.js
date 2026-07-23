// test_basic.js - Basic smoke test for Node.js bindings (SSTcore / sstcore)
'use strict';

const assert = require('assert');
const sst = require('../index.js');

function fail(msg) {
  console.error('FAIL:', msg);
  process.exit(1);
}

console.log('Testing SSTcore npm package...');
console.log('Version:', sst.version);
console.log('Available:', sst.isAvailable);
console.log('Is Native:', sst.isNative);
console.log('Is WASM:', sst.isWasm);
console.log('nativeAddonName:', sst.nativeAddonName);

if (!sst.isAvailable) {
  fail(sst.error || 'Module not available');
}

if (typeof sst.engineInfo !== 'function') {
  fail('engineInfo() missing');
}
const info = sst.engineInfo();
console.log('engineInfo:', JSON.stringify(info));
assert.strictEqual(info.engineVersion, '0.8.19', 'engineVersion must be 0.8.19');
assert.ok(info.canonVersion, 'canonVersion must be present');
assert.strictEqual(info.canonVersion, '0.8.20', 'canonVersion must be 0.8.20');
assert.strictEqual(info.packageVersion, '0.8.19', 'packageVersion must be 0.8.19');
assert.ok(info.numericProfile, 'numericProfile must be present');
assert.notStrictEqual(
  String(info.numericProfile).toLowerCase(),
  'fast',
  'default npm profile should not be fast',
);

if (typeof sst.getCapabilities !== 'function') {
  fail('getCapabilities() missing');
}
const caps = sst.getCapabilities();
console.log('getCapabilities:', JSON.stringify(caps));
assert.strictEqual(caps.biotSavart, true);
assert.strictEqual(caps.knotGeometry, true);
assert.strictEqual(caps.frenetHelicity, true);
assert.strictEqual(caps.magnusIntegrator, true);
assert.strictEqual(caps.sstIntegrator, true);
assert.strictEqual(caps.continuousReach, true);
assert.strictEqual(caps.polygonalGauss, true);
assert.strictEqual(caps.filamentVelocity, true);
assert.strictEqual(caps.filamentIntegrator, true);
assert.strictEqual(caps.topologyGuard, true);
assert.strictEqual(caps.intrinsicFrame, true);
assert.strictEqual(caps.rigidMotion, true);
assert.strictEqual(caps.resolvedTubeGeometry, true);

if (typeof sst.listBindings === 'function') {
  const lb = sst.listBindings();
  console.log('listBindings counts:', lb.counts);
  if (lb.functions.length) {
    console.log('Sample exports:', lb.functions.slice(0, 8).join(', '), '...');
  }
}

if (typeof sst.computeVelocity !== 'function') {
  fail('computeVelocity missing');
}
{
  const curve = [
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 0],
  ];
  const grid = [[0.5, 0.5, 0.5]];
  const result = sst.computeVelocity(curve, grid);
  assert.ok(result != null, 'computeVelocity returned null');
  console.log('✓ computeVelocity');
}

if (typeof sst.computeSstMass !== 'function') {
  fail('computeSstMass missing');
}
{
  const pts = [
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
  ];
  const m = sst.computeSstMass(pts, 1.0);
  console.log('✓ computeSstMass:', Array.isArray(m) ? m.join(', ') : m);
}

if (typeof sst.rk4Integrate !== 'function') {
  fail('rk4Integrate missing');
}
console.log('✓ rk4Integrate present');

if (typeof sst.computeWrithe === 'function') {
  const ring = [];
  for (let i = 0; i < 32; i++) {
    const t = (i / 32) * 2 * Math.PI;
    ring.push([Math.cos(t), Math.sin(t), 0]);
  }
  const w = sst.computeWrithe(ring);
  console.log('✓ computeWrithe (sample ring):', w);
} else {
  fail('computeWrithe missing');
}

console.log('\nBasic test completed OK');
process.exit(0);
