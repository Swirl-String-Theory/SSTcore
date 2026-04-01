/**
 * node_magnus_integrator.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.magnusIntegratorAvailable) {
        console.log('[SKIP] magnus_integrator');
        return;
    }
    const integ = sst.createMagnusBernoulliIntegrator(1.0, 1.0, 0.01, 1.0);
    const F = sst.magnusComputeForce(integ, [1, 0, 0], [0, 1, 0], 0.1, [0, 0, 0], [0, 0, 0]);
    console.log('magnusComputeForce:', F[0], F[1], F[2]);
}

main();
