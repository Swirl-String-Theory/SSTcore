/**
 * node_vorticity_dynamics.cpp — see examples/example_vorticity_transport.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.vorticityDynamicsAvailable) {
        console.log('[SKIP] vorticity_dynamics');
        return;
    }
    const w = sst.solidBodyRotationVorticity(2.0);
    console.log('solidBodyRotationVorticity:', w);
}

main();
