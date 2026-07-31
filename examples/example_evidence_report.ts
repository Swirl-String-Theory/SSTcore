/**
 * evidence_report_node.cpp — see examples/example_evidence_report.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || typeof sst.checkKindExportString !== 'function') {
        console.log('[SKIP] evidence_report: addon not available');
        return;
    }
    // CheckKind::SyntheticDiagnostic == 6
    console.log('checkKindExportString(6):', sst.checkKindExportString(6));

    const json = sst.buildEvidenceReportJson(sst.version || '0.8.28', sst.version || '0.8.28', [
        {
            name: 'demo_check',
            passed: true,
            kind: 0, // AlgebraicIdentity
            residual: 0,
            tolerance: 1e-12,
            supportsEmpiricalClaim: false,
            message: 'example',
        },
    ]);
    console.log('buildEvidenceReportJson:', json.slice(0, 120).replace(/\n/g, ' '), '...');
}

main();
