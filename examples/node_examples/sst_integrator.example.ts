/**
 * node_sst_integrator.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.sstIntegratorAvailable) {
        console.log('[SKIP] sst_integrator');
        return;
    }
    const pts = [
        [0, 0, 0],
        [1, 0, 0],
        [0.5, 0.8, 0],
    ];
    const mass = sst.computeSstMass(pts, 1.0);
    console.log('computeSstMass [m_core, m_fluid]:', mass[0], mass[1]);
}

main();
