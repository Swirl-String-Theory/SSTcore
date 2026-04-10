/**
 * node_knot.cpp
 */
const sst = require('../index.js');

function main() {
    if (!sst.isAvailable || !sst.knotAvailable) {
        console.log('[SKIP] knot');
        return;
    }
    const ring: number[][] = [];
    for (let i = 0; i < 32; i++) {
        const t = (i / 32) * 2 * Math.PI;
        ring.push([Math.cos(t), Math.sin(t), 0]);
    }
    console.log('writhe:', sst.computeWrithe(ring));
    const names = sst.getEmbeddedKnotFiles();
    console.log('embedded knot files count:', Object.keys(names).length);
}

main();
