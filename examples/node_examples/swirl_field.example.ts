/**
 * node_swirl_field.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.swirlFieldAvailable) {
        console.log('[SKIP] swirl_field');
        return;
    }
    const f = sst.computeSwirlField(8, 0.5);
    console.log('computeSwirlField length:', f.length);
}

main();
