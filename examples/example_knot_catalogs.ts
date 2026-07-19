/**
 * VortexLab-compatible JS knot catalogs (resources/knots_data_*.js).
 *
 * JS (after npm install):
 *   const { loadIdealCatalog } = require('sst-core/resources/load_knot_catalogs');
 *
 * TS (this example, from repo):
 *   import { loadIdealCatalog, ... } from '../resources/load_knot_catalogs';
 *
 * Native C++ paths (loadKnot / embedded ideal) remain the dynamics entry points;
 * these catalogs are the VortexLab metadata + Fourier coefficient databases.
 */
import {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
  catalogPaths,
} from '../resources/load_knot_catalogs';

function metaOf(entry: { knotId?: string; label?: string; components?: unknown[]; L?: number; D?: number } | undefined) {
  if (!entry) return null;
  return {
    knotId: entry.knotId,
    label: entry.label,
    components: Array.isArray(entry.components) ? entry.components.length : 0,
    L: entry.L,
    D: entry.D,
  };
}

function main() {
  const paths = catalogPaths();
  console.log('catalog paths:', paths);

  const ideal = loadIdealCatalog();
  const fseries = loadFseriesCatalog();
  const knotplot = loadKnotplotCatalog();

  console.log('ideal ids:', ideal.ids.length, 'sample:', ideal.ids.slice(0, 5));
  console.log('ideal 3:1:1:', metaOf(ideal.db['3:1:1']));

  console.log('fseries ids:', fseries.ids.length, 'sample:', fseries.ids.slice(0, 5));
  console.log('fseries 3_1:', metaOf(fseries.db['3_1']));

  console.log('knotplot ids:', knotplot.ids.length, 'sample:', knotplot.ids.slice(0, 5));
  console.log('knotplot knot_3.1:', metaOf(knotplot.db['knot_3.1']));
  console.log('knotplot torus_6.9:', metaOf(knotplot.db['torus_6.9']));

  console.log(
    'note: use sst.loadKnot / embedded ideal APIs for native dynamics; these JS catalogs mirror VortexLab selection UIs.',
  );
}

main();
