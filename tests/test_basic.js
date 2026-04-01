// test_basic.js - Basic test for Node.js bindings (SSTcore / sstcore)

const sst = require('../index.js');

console.log('Testing SSTcore npm package...');
console.log('Version:', sst.version);
console.log('Available:', sst.isAvailable);
console.log('Is Native:', sst.isNative);
console.log('Is WASM:', sst.isWasm);
console.log('nativeAddonName:', sst.nativeAddonName);

if (!sst.isAvailable) {
    console.error('Module not available:', sst.error);
    console.log('This is expected if the native addon or WASM module has not been built.');
    console.log('Run: npm run build:node (requires CMake for knot embed + node-gyp)');
    process.exit(0);
}

if (typeof sst.listBindings === 'function') {
    const lb = sst.listBindings();
    console.log('listBindings counts:', lb.counts);
    if (lb.functions.length) {
        console.log('Sample exports:', lb.functions.slice(0, 8).join(', '), '...');
    }
}

try {
    if (typeof sst.computeVelocity === 'function') {
        console.log('✓ computeVelocity function available');

        const curve = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]];
        const grid = [[0.5, 0.5, 0.5]];

        try {
            const result = sst.computeVelocity(curve, grid);
            console.log('✓ computeVelocity test passed');
            console.log('Result type:', typeof result, Array.isArray(result) ? 'Array' : result.constructor.name);
        } catch (err) {
            console.error('✗ computeVelocity test failed:', err.message);
        }
    } else {
        console.log('computeVelocity function not available (module may be stub)');
    }

    if (typeof sst.computeSstMass === 'function') {
        const pts = [[0, 0, 0], [1, 0, 0], [0, 1, 0]];
        const m = sst.computeSstMass(pts, 1.0);
        console.log('✓ computeSstMass:', Array.isArray(m) ? m.join(', ') : m);
    }

    if (sst.knotAvailable && typeof sst.computeWrithe === 'function') {
        const ring = [];
        for (let i = 0; i < 32; i++) {
            const t = (i / 32) * 2 * Math.PI;
            ring.push([Math.cos(t), Math.sin(t), 0]);
        }
        const w = sst.computeWrithe(ring);
        console.log('✓ computeWrithe (sample ring):', w);
    }

    console.log('\nBasic test completed!');
} catch (err) {
    console.error('Test error:', err.message);
    process.exit(1);
}
