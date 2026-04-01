/**
 * node_ab_initio.cpp — particle zoo / ParticleEvaluator
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.abInitioAvailable) {
        console.log('[SKIP] ab_initio');
        return;
    }
    try {
        const m = sst.zooGetEntryMass('electron');
        console.log('zooGetEntryMass(electron):', m);
    } catch (e) {
        console.log('zooGetEntryMass:', (e).message);
    }
}

main();
