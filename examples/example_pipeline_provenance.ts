/**
 * pipeline_provenance_node.cpp — see examples/example_pipeline_provenance.py
 */
const sst = require('../index.js');

function baseRecord(extra) {
    return Object.assign(
        {
            stage: 0, // KnotPlot
            certification: 1, // Candidate
            toolName: 'tool',
            toolVersion: '1',
            inputSha256: 'in',
            outputSha256: 'out',
            parameterSha256: 'par',
            parentRecordSha256: '',
            coordinateConvention: 'xyz',
            scaleConvention: 'R=1',
            timestampUtc: '2026-01-01T00:00:00Z',
        },
        extra || {}
    );
}

function main() {
    if (!sst.isAvailable || typeof sst.evaluateProvenanceChain !== 'function') {
        console.log('[SKIP] pipeline_provenance: addon not available');
        return;
    }
    const a = baseRecord({ inputSha256: 'a0', outputSha256: 'a1', parentRecordSha256: '' });
    const fp = sst.provenanceRecordFingerprint(a);
    console.log('provenanceRecordFingerprint:', fp);

    const b = baseRecord({
        stage: 3, // SSTcore
        inputSha256: 'a1',
        outputSha256: 'a2',
        parentRecordSha256: fp,
    });
    const status = sst.evaluateProvenanceChain([a, b]);
    console.log('evaluateProvenanceChain:', status);
}

main();
