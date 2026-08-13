/**
 * sst_action_phase_node.cpp — see examples/example_action_phase.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.massShellHamiltonian !== 'function') {
        console.log('[SKIP] action_phase: addon not available');
        return;
    }
    const P = 3.0;
    const E0 = 4.0;
    const c = 1.0;
    const Omega0 = 2.0;
    console.log('massShellHamiltonian:', sst.massShellHamiltonian(P, E0, c));
    console.log('velocityFromMassShell:', sst.velocityFromMassShell(P, E0, c));
    console.log('gammaFromMassShell:', sst.gammaFromMassShell(P, E0, c));
    console.log('properTimeRate:', sst.properTimeRate(P, E0, c));
    console.log(
        'internalPhaseRateAtFixedMomentum:',
        sst.internalPhaseRateAtFixedMomentum(P, E0, c, Omega0)
    );
    const r = sst.actionPhaseResiduals(P, E0, c, Omega0);
    console.log('actionPhaseResiduals ok=', r.ok, 'H_res=', r.hamiltonianConsistency);
}

main();
