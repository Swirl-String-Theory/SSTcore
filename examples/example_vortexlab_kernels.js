/**
 * Smoke: VortexLab kernel Node exports (run after native build).
 *   node examples/example_vortexlab_kernels.js
 */
const path = require('path');

function load() {
  try {
    return require('..');
  } catch (_) {
    const candidates = [
      path.join(__dirname, '..', 'build', 'Release', 'sstcore.node'),
      path.join(__dirname, '..', 'cmake-build-release', 'sstcore.node'),
      path.join(__dirname, '..', 'build_node', 'Release', 'sstcore.node'),
    ];
    for (const c of candidates) {
      try {
        return require(c);
      } catch (_) {}
    }
    throw new Error('sstcore native addon not found; build Node target first');
  }
}

function circle(n, R = 1, z = 0) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const t = (2 * Math.PI * i) / n;
    pts.push([R * Math.cos(t), R * Math.sin(t), z]);
  }
  return pts;
}

const sst = load();
const caps = sst.getCapabilities();
console.log('continuousReach', caps.continuousReach);
console.log('polygonalGauss', caps.polygonalGauss);

const c = circle(64);
const resampled = sst.resampleClosedCurve(c, 128);
console.log('resampled', resampled.length);

const reach = sst.computeContinuousReach([circle(96)]);
console.log('reach', reach.reach, reach.limiter);

const pair = sst.computeContinuousReach([circle(64, 1, -0.4), circle(64, 1, 0.4)]);
console.log('pair reach', pair.reach, pair.limiter);

const g = sst.computePolygonalGauss(circle(48));
console.log('writhe signed', g.signedIntegral);

console.log('ok');
