/**
 * node_fluid_dynamics.cpp — see examples/example_fluid_rotation.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable) {
        console.log('[SKIP] fluid_dynamics');
        return;
    }
    const vel = new Float64Array([1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1]);
    const mag = sst.computeVelocityMagnitude(vel);
    console.log('velocity magnitude (2x2x2):', mag.slice(0, 4));
}

main();
