/**
 * node_frenet_helicity.cpp — see examples/HelicityCalculation.py
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable) {
        console.log('[SKIP] frenet_helicity');
        return;
    }
    const pts = [];
    for (let i = 0; i < 16; i++) {
        const t = (i / 16) * 2 * Math.PI;
        pts.push([Math.cos(t), Math.sin(t), 0.1 * Math.sin(2 * t)]);
    }
    const fr = sst.computeFrenetFrames(pts);
    console.log('Frenet T length:', fr.T.length);
}

main();
