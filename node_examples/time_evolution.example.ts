/**
 * node_time_evolution.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.timeEvolutionAvailable) {
        console.log('[SKIP] time_evolution');
        return;
    }
    const pos = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
    ];
    const tan = [
        [1, 0, 0],
        [0, 1, 0],
        [-1, 0, 0],
    ];
    const te = new sst.TimeEvolution(pos, tan, 1.0);
    te.evolve(0.01, 2);
    const p2 = te.getPositions();
    console.log('TimeEvolution positions length:', p2.length);
}

main();
