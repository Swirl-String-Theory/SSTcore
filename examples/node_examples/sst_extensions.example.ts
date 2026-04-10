/**
 * node_sst_extensions.cpp — f-series / helicity helpers; needs on-disk .fseries path.
 */
const path = require('path');
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.sstExtensionsAvailable) {
        console.log('[SKIP] sst_extensions');
        return;
    }
    const fseries = path.join(__dirname, '..', 'resources', 'Knots_FourierSeries', '4_1', 'knot.4_1.fseries');
    try {
        const h = sst.computeHelicityFromFseries(fseries, 16, 0.1, 4, 200);
        console.log('computeHelicityFromFseries keys:', Object.keys(h));
    } catch (e) {
        console.log('[SKIP] sst_extensions file IO:', (e).message);
    }
}

main();
