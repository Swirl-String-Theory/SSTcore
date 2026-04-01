/**
 * node_sst_gravity.cpp — see examples/example_sst_gravity.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.sstGravityAvailable) {
        console.log('[SKIP] sst_gravity');
        return;
    }
    const B = [
        [1, 0, 0],
        [0, 1, 0],
    ];
    const C = [
        [0, 0, 1],
        [0, 0, 1],
    ];
    const shear = sst.sstGravityBeltramiShear(B, C);
    console.log('sstGravityBeltramiShear length:', shear.length);
}

main();
