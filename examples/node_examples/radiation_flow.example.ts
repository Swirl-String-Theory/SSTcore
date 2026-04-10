/**
 * node_radiation_flow.cpp — see examples/example_radiation_flow.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.radiationFlowAvailable) {
        console.log('[SKIP] radiation_flow');
        return;
    }
    const f = sst.radiationForce(1, 1, 0.5, 0.5, 0.1);
    console.log('radiationForce:', f);
}

main();
