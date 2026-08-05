'use strict';

/**
 * Node resource-path smoke tests (deelplan res-1 / res-4).
 * Run via: node tests/test_resource_paths.js
 */

const path = require('path');
const assert = require('assert');

const root = path.join(__dirname, '..');
const { createResourceHelpers } = require('../lib/resource_helpers');

const helpers = createResourceHelpers(root, {});
const { camel } = helpers;

assert.ok(camel.getResourcesDir(), 'getResourcesDir');
const ideal = camel.getIdealTxtPath();
assert.ok(ideal, 'getIdealTxtPath');
assert.ok(ideal.replace(/\\/g, '/').includes('/ideal/ideal.txt') || ideal.endsWith('ideal.txt'));

const kpDir = camel.getKnotplotDir();
assert.ok(kpDir, 'getKnotplotDir');

if (camel.listKnotplotIds) {
  const ids = camel.listKnotplotIds();
  assert.ok(Array.isArray(ids) && ids.includes('knot_3.1'), 'listKnotplotIds');
  const ab = camel.getKnotplotAbPath('knot_3.1');
  assert.ok(ab && ab.endsWith('_ab.xml'), 'getKnotplotAbPath');
  assert.ok(camel.getKnotplotAb('knot_3.1'), 'getKnotplotAb');
  assert.strictEqual(camel.normalizeKnotplotId('3.1'), 'knot_3.1');
}

console.log('test_resource_paths.js OK');
