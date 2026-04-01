/**
 * node_thermo_dynamics.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.thermoDynamicsAvailable) {
        console.log('[SKIP] thermo_dynamics');
        return;
    }
    const theta = sst.potentialTemperature(300, 100000, 95000, 287, 1004);
    console.log('potentialTemperature:', theta);
}

main();
