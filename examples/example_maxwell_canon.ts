/** Smoke example: ideal regime + projector + Maxwell stack. */
const sst = require('../index.js');
if (!sst || !sst.available) {
  console.log('[SKIP] native addon unavailable');
  process.exit(0);
}
console.log('evaluateWorldsheetGuards', sst.evaluateWorldsheetGuards && sst.evaluateWorldsheetGuards(3, 1.0, 1e-8, false, false));
console.log('evaluateIdealKnotRegime', sst.evaluateIdealKnotRegime && sst.evaluateIdealKnotRegime(1, 1, 1, 1, 0, 0));
console.log('projectorSphereIntegral', sst.projectorSphereIntegral && sst.projectorSphereIntegral());
console.log('leadingResponseR0', sst.leadingResponseR0 && sst.leadingResponseR0(16.3714672385));
console.log('maxwellThreeGate', sst.maxwellThreeGate && sst.maxwellThreeGate(1, 2, 1, 0.1, 1));
console.log('evaluateMechanicalFalsifier', sst.evaluateMechanicalFalsifier && sst.evaluateMechanicalFalsifier(2, 1, 7e-7, 1));
console.log('evaluateSwirlTonic', sst.evaluateSwirlTonic && sst.evaluateSwirlTonic([1],[0],[0],[1],[0],[0], 1, false));
