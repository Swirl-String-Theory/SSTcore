'use strict';
const assert = require('assert');
const sst = require('../index.js');

assert.ok(typeof sst.massShellHamiltonian === 'function');
assert.ok(Math.abs(sst.massShellHamiltonian(3, 4, 1) - 5) < 1e-12);
assert.ok(Math.abs(sst.gammaFromMassShell(3, 4, 1) - 1.25) < 1e-12);
assert.ok(Math.abs(sst.properTimeRate(0, 2, 1) - 1) < 1e-12);
const r = sst.actionPhaseResiduals(3, 4, 1, 2);
assert.strictEqual(r.ok, true);
assert.ok(r.hamiltonianConsistency < 1e-12);
console.log('✓ test_action_phase.js');
