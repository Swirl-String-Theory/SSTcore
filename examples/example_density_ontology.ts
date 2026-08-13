/** Smoke example: density ontology + rotor + scaling (Canon 0.8.30–0.8.32). */
const sst = require('../index.js');
if (!sst || !sst.available) {
  console.log('[SKIP] native addon unavailable');
  process.exit(0);
}
const form = sst.validateEnergyDensityForm ? sst.validateEnergyDensityForm(2) : null;
console.log('validateEnergyDensityForm', form);
console.log('evaluateRotorParticipation', sst.evaluateRotorParticipation && sst.evaluateRotorParticipation());
console.log('rhoRefLegacy', sst.rhoRefLegacy && sst.rhoRefLegacy());
console.log('classifyObservableScaling(acceleration)', sst.classifyObservableScaling && sst.classifyObservableScaling('acceleration'));
