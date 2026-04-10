/**
 * node_potential_timefield.cpp — timefield / gravitational potential
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.timeFieldAvailable) {
        console.log('[SKIP] potential_timefield');
        return;
    }
    const pos = [[0, 0, 0], [1, 0, 0]];
    const vor = [[0, 0, 1], [0, 0, 1]];
    const phi = sst.computeGravitationalPotential(pos, vor, 1e-6);
    console.log('computeGravitationalPotential:', phi);
}

main();
