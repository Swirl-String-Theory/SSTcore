/**
 * operational_spacetime_node.cpp — see examples/example_operational_spacetime.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.radarInterval !== 'function') {
        console.log('[SKIP] operational_spacetime: addon not available');
        return;
    }
    const radar = sst.radarInterval(1.0, 3.0, 1.0);
    console.log('radarInterval:', radar.causal, radar.radarTime, radar.radarDistance);

    const boost = sst.lorentzBoostX([2.0, 1.0, 0.0, 0.0], 0.6, 1.0);
    console.log('lorentzBoostX gamma=', boost.gamma, 'residual=', boost.invariantResidual);
}

main();
