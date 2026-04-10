/**
 * node_hyperbolic_volume.cpp — see examples/knot_pd_and_volume_example.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.hyperbolicVolumeAvailable) {
        console.log('[SKIP] hyperbolic_volume');
        return;
    }
    const unknotPd: number[][] = [[1, 2, 1, 2]];
    const v = sst.hyperbolicVolumeFromPd(unknotPd);
    console.log('hyperbolicVolumeFromPd (toy PD):', v);
}

main();
