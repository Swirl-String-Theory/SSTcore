/**
 * node_field_kernels.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.fieldKernelsAvailable) {
        console.log('[SKIP] field_kernels');
        return;
    }
    const B = sst.dipoleFieldAtPoint([[0, 0, 1]], [[0, 0, 1]]);
    console.log('dipoleFieldAtPoint:', B[0], B[1], B[2]);
}

main();
