'use strict';

/**
 * Node loader for VortexLab-compatible knot catalog scripts in this directory:
 *   knots_data_ideal.js    → IDEAL_KNOT_IDS / IDEAL_KNOT_DB
 *   knots_data_fourier.js  → FSERIES_KNOT_IDS / FSERIES_KNOT_DB
 *   knots_data_knotplot.js → KNOTPLOT_KNOT_IDS / KNOTPLOT_KNOT_DB
 *
 * These files use top-level `const` (browser script style). This module evaluates
 * them in a sandbox and returns { source, ids, db } without rewriting the data files.
 *
 * Usage (CJS):
 *   const { loadIdealCatalog } = require('sst-core/resources/load_knot_catalogs');
 *
 * Usage (TS / tsx from repo):
 *   import { loadFseriesCatalog } from '../resources/load_knot_catalogs';
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = __dirname;

const CATALOG_FILES = {
  ideal: {
    file: 'knots_data_ideal.js',
    idsName: 'IDEAL_KNOT_IDS',
    dbName: 'IDEAL_KNOT_DB',
  },
  fseries: {
    file: 'knots_data_fourier.js',
    idsName: 'FSERIES_KNOT_IDS',
    dbName: 'FSERIES_KNOT_DB',
  },
  knotplot: {
    file: 'knots_data_knotplot.js',
    idsName: 'KNOTPLOT_KNOT_IDS',
    dbName: 'KNOTPLOT_KNOT_DB',
  },
};

/**
 * @param {'ideal'|'fseries'|'knotplot'} source
 * @returns {{ source: string, ids: string[], db: Record<string, object> }}
 */
function loadCatalog(source) {
  const spec = CATALOG_FILES[source];
  if (!spec) {
    throw new Error(`Unknown knot catalog source: ${source}`);
  }
  const filePath = path.join(ROOT, spec.file);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Knot catalog file missing: ${filePath}`);
  }
  const code = fs.readFileSync(filePath, 'utf8');
  const sandbox = {
    window: {},
    console,
  };
  // Same-script expression reads top-level const bindings after the catalog body.
  const wrapped =
    `${code}\n;` +
    `({ ids: typeof ${spec.idsName} !== 'undefined' ? ${spec.idsName} : ` +
    `(typeof window !== 'undefined' && window.${spec.idsName}) || [], ` +
    `db: typeof ${spec.dbName} !== 'undefined' ? ${spec.dbName} : ` +
    `(typeof window !== 'undefined' && window.${spec.dbName}) || {} })`;

  const result = vm.runInNewContext(wrapped, sandbox, {
    filename: filePath,
    timeout: 60000,
  });

  const ids = Array.isArray(result && result.ids) ? result.ids.slice() : [];
  const db =
    result && result.db && typeof result.db === 'object' && !Array.isArray(result.db)
      ? result.db
      : {};

  return { source, ids, db };
}

function loadIdealCatalog() {
  return loadCatalog('ideal');
}

function loadFseriesCatalog() {
  return loadCatalog('fseries');
}

function loadKnotplotCatalog() {
  return loadCatalog('knotplot');
}

function loadAllKnotCatalogs() {
  return {
    ideal: loadIdealCatalog(),
    fseries: loadFseriesCatalog(),
    knotplot: loadKnotplotCatalog(),
  };
}

function catalogPaths() {
  return {
    ideal: path.join(ROOT, CATALOG_FILES.ideal.file),
    fseries: path.join(ROOT, CATALOG_FILES.fseries.file),
    knotplot: path.join(ROOT, CATALOG_FILES.knotplot.file),
  };
}

module.exports = {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
  loadAllKnotCatalogs,
  catalogPaths,
  CATALOG_FILES,
};
