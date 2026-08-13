/**
 * geometry_certificate_node.cpp — see examples/example_geometry_certificate.py
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
    if (!sst.isAvailable || typeof sst.evaluateTubeGeometry !== 'function') {
        console.log('[SKIP] geometry_certificate: addon not available');
        return;
    }
    const ring = circle(64);
    const geom = sst.evaluateTubeGeometry(ring, 0.05);
    console.log('evaluateTubeGeometry:', geom.status, 'sep=', geom.minimumSeparation);

    const under = sst.evaluateContactSaturation([0.4, 0.1], 1.0);
    console.log('evaluateContactSaturation:', under.status, under.saturationRatio);

    const hit = sst.chronosFirstHitting([0, 1, 2], [0, 0.5, 1.5], 1.0);
    console.log('chronosFirstHitting:', hit.status, hit.firstHittingTime);

    const rank = sst.rank9FromSingularValues([9, 8, 7, 6, 5, 4, 3, 2, 1]);
    console.log('rank9FromSingularValues:', rank.status, rank.numericalRank);
}

main();
