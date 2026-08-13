/**
 * value_origin_node.cpp — see examples/example_value_origin.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.fmaxSnapshot !== 'function') {
        console.log('[SKIP] value_origin: addon not available');
        return;
    }
    console.log('fmaxSnapshot:', sst.fmaxSnapshot());
    const cmp = sst.compareFmaxSnapshotToRecomputed();
    console.log('compareFmaxSnapshotToRecomputed:', cmp.snapshot, cmp.recomputed, cmp.snapshotUnchanged);
    console.log('bareMassRatioFromDimensionlessLength(16.3716):', sst.bareMassRatioFromDimensionlessLength(16.3716));
}

main();
