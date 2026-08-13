/**
 * sst_kam_diagnostics_node.cpp — see examples/example_kam_diagnostics.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.kamStage1 !== 'function') {
        console.log('[SKIP] kam_diagnostics: addon not available');
        return;
    }
    const r = sst.kamStage1(true, [1.0, Math.SQRT2], [2, 0, 0, 3], 1e-4);
    console.log('kamStage1:', r.status, r.achievedStage, 'det=', r.hessianDeterminant);

    const phi = 0.5 * (1 + Math.sqrt(5));
    console.log('goldenRatioNullTest:', sst.goldenRatioNullTest(phi), sst.goldenRatioNullTest(1.5));
}

main();
