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
assert.strictEqual(info.engineVersion, '0.8.28', 'engineVersion must be 0.8.28');
assert.ok(info.canonVersion, 'canonVersion must be present');
assert.strictEqual(info.canonVersion, '0.8.28', 'canonVersion must equal package (Optie A)');
assert.strictEqual(info.packageVersion, '0.8.28', 'packageVersion must be 0.8.28');
assert.strictEqual(info.canonVersion, info.packageVersion, 'canonVersion must equal packageVersion');
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
assert.strictEqual(caps.geometryCertificate, true);
assert.strictEqual(caps.polygonalSmoothCertificate, true);
assert.strictEqual(caps.biotSavartGate, true);
assert.strictEqual(caps.operationalSpacetime, true);
assert.strictEqual(caps.qssSpectroscopy, true);
assert.strictEqual(caps.pipelineProvenance, true);
assert.strictEqual(caps.coreTorsion, true);
assert.strictEqual(caps.linkFieldGate, true);
assert.strictEqual(caps.kamDiagnostics, true);
assert.strictEqual(caps.valueOrigin, true);
assert.strictEqual(caps.evidenceReport, true);
assert.strictEqual(caps.actionPhase, true);

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

if (typeof sst.evaluateContactSaturation !== 'function') {
  fail('evaluateContactSaturation missing');
}
{
  const under = sst.evaluateContactSaturation([0.4], 1.0);
  assert.strictEqual(under.status, 'Pass');
  const over = sst.evaluateContactSaturation([1.2], 1.0);
  assert.strictEqual(over.status, 'Fail');
  console.log('✓ evaluateContactSaturation');
}

if (typeof sst.chronosFirstHitting !== 'function') {
  fail('chronosFirstHitting missing');
}
{
  const hit = sst.chronosFirstHitting([0, 1, 2], [0, 0.5, 1.5], 1.0);
  assert.strictEqual(hit.status, 'Pass');
  assert.ok(Math.abs(hit.firstHittingTime - 1.5) < 1e-12);
  const miss = sst.chronosFirstHitting([0, 1, 2], [0, 0.2, 0.4], 1.0);
  assert.strictEqual(miss.status, 'Fail');
  console.log('✓ chronosFirstHitting');
}

if (typeof sst.rank9FromSingularValues !== 'function') {
  fail('rank9FromSingularValues missing');
}
{
  const full = sst.rank9FromSingularValues([9, 8, 7, 6, 5, 4, 3, 2, 1]);
  assert.strictEqual(full.status, 'Pass');
  assert.strictEqual(full.numericalRank, 9);
  const short = sst.rank9FromSingularValues([9, 8, 7, 6, 5, 4, 3, 2, 0]);
  assert.strictEqual(short.status, 'Fail');
  assert.strictEqual(short.numericalRank, 8);
  console.log('✓ rank9FromSingularValues');
}

if (typeof sst.evaluateTubeGeometry !== 'function') {
  fail('evaluateTubeGeometry missing');
}
{
  const ring = [];
  for (let i = 0; i < 64; i++) {
    const t = (i / 64) * 2 * Math.PI;
    ring.push([Math.cos(t), Math.sin(t), 0]);
  }
  const pass = sst.evaluateTubeGeometry(ring, 0.05);
  assert.strictEqual(pass.status, 'Pass');
  const failGeom = sst.evaluateTubeGeometry(ring, 2.0);
  assert.strictEqual(failGeom.status, 'Fail');
  console.log('✓ evaluateTubeGeometry');
}

if (typeof sst.evaluatePolygonalSmoothCertificate !== 'function') {
  fail('evaluatePolygonalSmoothCertificate missing');
}
{
  const ring = [];
  for (let i = 0; i < 48; i++) {
    const t = (i / 48) * 2 * Math.PI;
    ring.push([Math.cos(t), Math.sin(t), 0]);
  }
  // Diagnostic-only: Pass reserved for reach/isotopy (audit H-004).
  const ok = sst.evaluatePolygonalSmoothCertificate(ring, ring, 0.05, 1e-9, 1e-9, 1e-6);
  assert.strictEqual(ok.status, 'Indeterminate');
  const scaled = [];
  for (let i = 0; i < 64; i++) {
    const t = (i / 64) * 2 * Math.PI;
    scaled.push([1.5 * Math.cos(t), 1.5 * Math.sin(t), 0]);
  }
  const coarse = sst.evaluatePolygonalSmoothCertificate(ring, scaled, 0.05, 0.01, 0.01, 0.01);
  assert.strictEqual(coarse.status, 'Fail');
  console.log('✓ evaluatePolygonalSmoothCertificate');
}

if (typeof sst.evaluateBiotSavartGate !== 'function') {
  fail('evaluateBiotSavartGate missing');
}
{
  const aK = 1 / (4 * Math.PI);
  const ok = sst.evaluateBiotSavartGate(aK, 0, 1.0, 0.1, 128, 'desing_core_v1', 1e-12, true);
  assert.strictEqual(ok.status, 'Pass');
  const missing = sst.evaluateBiotSavartGate(aK, 0, 1.0, 0.1, 128, '', 1e-12, true);
  assert.strictEqual(missing.status, 'Indeterminate');
  console.log('✓ evaluateBiotSavartGate');
}

if (typeof sst.radarInterval !== 'function') {
  fail('radarInterval missing');
}
{
  const r = sst.radarInterval(1.0, 3.0, 1.0);
  assert.strictEqual(r.causal, true);
  assert.ok(Math.abs(r.radarTime - 2.0) < 1e-12);
  console.log('✓ radarInterval');
}

if (typeof sst.qssEigen2x2 !== 'function') {
  fail('qssEigen2x2 missing');
}
{
  const r = sst.qssEigen2x2([2, 0, 0, 5]);
  assert.strictEqual(r.epistemicStatus, 'SYNTHETIC_DIAGNOSTIC');
  console.log('✓ qssEigen2x2');
}

if (typeof sst.torsionInertialMass !== 'function') {
  fail('torsionInertialMass missing');
}
{
  const r = sst.torsionInertialMass(2.0, 3.0, 1.0);
  assert.strictEqual(r.ok, true);
  assert.ok(Math.abs(r.mass - 6.0) < 1e-12);
  const legacy = sst.torsionInertialMassLegacyFactor2(2.0, 3.0, 1.0);
  assert.ok(Math.abs(legacy.mass - 12.0) < 1e-12);
  console.log('✓ torsionInertialMass');
}

if (typeof sst.kamStage1 !== 'function') fail('kamStage1 missing');
{
  const r = sst.kamStage1(true, [1.0, Math.SQRT2], [2,0,0,3], 1e-4);
  assert.strictEqual(r.status, 'Pass');
  console.log('✓ kamStage1');
}

if (typeof sst.fmaxSnapshot !== 'function') fail('fmaxSnapshot missing');
{
  assert.ok(Math.abs(sst.fmaxSnapshot() - 29.053507) < 1e-9);
  assert.ok(Math.abs(sst.bareMassRatioFromDimensionlessLength(16.3716) - 4.0929) < 1e-6);
  console.log('✓ fmaxSnapshot/bareMass');
}

if (typeof sst.checkKindExportString !== 'function') fail('checkKindExportString missing');
{
  assert.strictEqual(sst.checkKindExportString(6), 'SYNTHETIC_DIAGNOSTIC');
  console.log('✓ checkKindExportString');
}

if (typeof sst.massShellHamiltonian !== 'function') fail('massShellHamiltonian missing');
{
  assert.ok(Math.abs(sst.massShellHamiltonian(3,4,1) - 5) < 1e-12);
  console.log('✓ massShellHamiltonian');
}

console.log('\nBasic test completed OK');
process.exit(0);
