/**
 * node_field_ops.cpp — curl3dCentral
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.fieldOpsAvailable) {
        console.log('[SKIP] field_ops');
        return;
    }
    const n = 2;
    const vel = new Float64Array(n * n * n * 3);
    for (let i = 0; i < vel.length; i++) vel[i] = 0.01 * i;
    const w = sst.curl3dCentral(vel, n, n, n, 0.1);
    console.log('curl first 3:', w[0], w[1], w[2]);
}

main();
