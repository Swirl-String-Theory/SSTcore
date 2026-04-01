/**
 * node_biot_savart.cpp — see examples/example_biot_savart.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable) {
        console.log('[SKIP] biot_savart: addon not available');
        return;
    }
    const curve = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
    ];
    const grid = [[0.5, 0.5, 0.5]];
    const v = sst.computeVelocity(curve, grid);
    console.log('computeVelocity sample:', v[0], v[1], v[2]);
}

main();
