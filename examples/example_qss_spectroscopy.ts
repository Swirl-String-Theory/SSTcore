/**
 * qss spectroscopy (via operational_spacetime_node / qss bind) — see examples/example_qss_spectroscopy.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.qssEigen2x2 !== 'function') {
        console.log('[SKIP] qss_spectroscopy: addon not available');
        return;
    }
    const r = sst.qssEigen2x2([2, 0, 0, 5]);
    console.log('qssEigen2x2:', r.epistemicStatus, 'residual=', r.eigenResidual, r.eigenvalues);
}

main();
