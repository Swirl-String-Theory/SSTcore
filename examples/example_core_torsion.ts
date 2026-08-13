/**
 * core_torsion_node.cpp — see examples/example_core_torsion.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.torsionInertialMass !== 'function') {
        console.log('[SKIP] core_torsion: addon not available');
        return;
    }
    const m = sst.torsionInertialMass(2.0, 3.0, 1.0);
    console.log('torsionInertialMass:', m.ok, m.mass, m.convention);

    const legacy = sst.torsionInertialMassLegacyFactor2(2.0, 3.0, 1.0);
    console.log('torsionInertialMassLegacyFactor2:', legacy.ok, legacy.mass);

    const gate = sst.evaluateLinkFieldGate(1.0, 2.0, 3.0, 0.0);
    console.log('evaluateLinkFieldGate:', gate.passed, gate.failure, gate.epistemicStatus);
}

main();
