/**
 * node_vortex_ring.cpp — see examples/example_vortex_ring.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.vortexRingAvailable) {
        console.log('[SKIP] vortex_ring');
        return;
    }
    const v = sst.lambOseenVelocity(0.1, 0.05, 1e-3, 1.0);
    console.log('lambOseenVelocity:', v);
    const nls = new sst.GoldenNLSClosure(sst.densityRegimeCoreDominated);
    console.log('GoldenNLSClosure loop mass @ R=1:', nls.calculateLoopMass(1.0));
}

main();
