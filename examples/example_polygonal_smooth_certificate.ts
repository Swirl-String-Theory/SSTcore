/**
 * polygonal_smooth_certificate_node.cpp — see examples/example_polygonal_smooth_certificate.py
 */
const sst = require('../index.js');

function circle(n, r = 1.0) {
    const pts = [];
    for (let i = 0; i < n; i++) {
        const t = (i / n) * 2 * Math.PI;
        pts.push([r * Math.cos(t), r * Math.sin(t), 0]);
    }
    return pts;
}

function main() {
    if (!sst.isAvailable || typeof sst.evaluatePolygonalSmoothCertificate !== 'function') {
        console.log('[SKIP] polygonal_smooth_certificate: addon not available');
        return;
    }
    const ring = circle(48);
    const cert = sst.evaluatePolygonalSmoothCertificate(ring, ring, 0.05, 1e-9, 1e-9, 1e-6);
    console.log('evaluatePolygonalSmoothCertificate:', cert.status, 'hausdorff=', cert.hausdorffBound);

    const aK = 1 / (4 * Math.PI);
    const biot = sst.evaluateBiotSavartGate(aK, 0, 1.0, 0.1, 128, 'desing_core_v1', 1e-12, true);
    console.log('evaluateBiotSavartGate:', biot.status, 'residual=', biot.relativeResidual);
}

main();
