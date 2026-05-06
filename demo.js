// demo.js in C:\workspace\projects\SSTcore
const sst = require('./'); // or './build/Release/sstcore.node'

// Example: check version and call one function
console.log('Version:', sst.version);
console.log('Is native?', sst.isNative, 'Is WASM?', sst.isWasm);

// Replace this with a real call you care about:
console.log('Exports:', Object.keys(sst));