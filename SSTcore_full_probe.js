#!/usr/bin/env node
/**
 * SSTcore_full_probe.js
 *
 * Full diagnostic probe for the official SSTcore npm package (Node native addon).
 *
 * Primary load style:
 *   const sst = require('./index.js');   // local checkout
 *   const sst = require('sst-core');     // published package
 *
 * Typical local usage:
 *   node SSTcore_full_probe.js
 *   node SSTcore_full_probe.js --json-out sstcore_probe_report_node.json
 *   node SSTcore_full_probe.js --install
 *   node SSTcore_full_probe.js --run-binding-tests
 *
 * Companion to SSTcore_full_probe.py (same diagnostic intent; camelCase N-API surface).
 * No SST claims are filled into any falsification matrix; this is capability testing only.
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
  catalogPaths,
} = require('./resources/load_knot_catalogs');

// ---------------------------------------------------------------------
// Canon-v0.8.x constants used only for numerical sanity checks.
// ---------------------------------------------------------------------

const SST_CONSTANTS = {
  v_swirl_m_s: 1.09384563e6,
  r_c_m: 1.40897017e-15,
  rho_f_kg_m3: 7.0e-7,
  rho_core_kg_m3: 3.8934358266918687e18,
  rho_E_J_m3: 3.49924562e35,
  c_m_s: 299792458.0,
  joule_per_MeV: 1.602176634e-13,
};

const TOPOLOGY_CANDIDATES = [
  ['trefoil', 'AB', '3:1:1'],
  ['figure_eight', 'AB', '4:1:1'],
  ['cinquefoil_torus', 'AB', '5:1:1'],
  ['up_quark_candidate_5_2', 'AB', '5:2:1'],
  ['down_quark_candidate_6_1', 'AB', '6:1:1'],
  ['hopf_link', 'LINK', 'L2a1'],
  ['solomon_link', 'LINK', 'L4a1'],
];

/** Node-facing helpers expected on the addon / package surface. */
const EXPECTED_NODE_HELPERS = [
  'engineInfo',
  'getCapabilities',
  'listBindings',
  'getEmbeddedKnotFiles',
  'getEmbeddedIdealFiles',
  'loadKnot',
  'loadEmbeddedIdealText',
  'parseEmbeddedIdealAbById',
  'parseFseriesMulti',
  'parseFseriesFromString',
  'evaluateFourierBlock',
  'lengthExact',
  'computeWrithe',
  'computeSstMass',
  'computeVelocity',
  'ParticleEvaluator',
  'ZooEvaluator',
  // Python-parity resource helpers (JS layer on index.js)
  'get_resources_dir',
  'get_ideal_txt_path',
  'get_knots_fourier_series_dir',
  'get_knotplot_dir',
  'get_ideal_ab',
  'get_ideal_link',
  'list_ideal_source_files',
  'list_embedded_fseries_ids',
  'load_fseries_knot',
  'knotplot',
  'resolve_knot_ref',
];

/** Formerly Python-only; kept empty so reports stay comparable if we reintroduce gaps. */
const PYTHON_ONLY_HELPERS = [];

const FSERIES_PROBE_LABELS = ['3_1', '4_1', '5_2', '6_1'];
const CANON_TREFOIL_ROPELENGTH = 16.371637;
const TREFOIL_EXPORT_SAMPLES = 128;

const TREFOIL_TRIAD_CHANNELS = [
  {
    channel: 'ideal_txt',
    ref: '3:1:1',
    source: 'ideal',
    expect_particle_evaluator: 'ok',
  },
  {
    channel: 'fremlin_fseries',
    ref: '3_1',
    source: 'fremlin',
    expect_particle_evaluator: 'skip',
  },
  {
    channel: 'knotplot_ideal',
    ref: 'knot_3.1',
    source: 'knotplot',
    expect_particle_evaluator: 'reject',
  },
];

const PROBE_ROOT = path.resolve(__dirname);

// ---------------------------------------------------------------------
// Small utilities
// ---------------------------------------------------------------------

function nowIso() {
  return new Date().toISOString();
}

function safeRepr(value, maxLen = 800) {
  let text;
  try {
    if (typeof value === 'string') text = value;
    else text = JSON.stringify(value);
    if (text === undefined) text = String(value);
  } catch (exc) {
    text = `<repr failed: ${exc && exc.name}: ${exc && exc.message}>`;
  }
  if (text.length > maxLen) return `${text.slice(0, maxLen)}... <truncated>`;
  return text;
}

function jsonable(value) {
  if (value === null || value === undefined) return value;
  const t = typeof value;
  if (t === 'boolean' || t === 'number' || t === 'string') return value;
  if (Array.isArray(value)) return value.map(jsonable);
  if (t === 'object') {
    if (Buffer.isBuffer(value)) return `<Buffer len=${value.length}>`;
    if (ArrayBuffer.isView(value)) {
      return { typedArray: value.constructor.name, length: value.length };
    }
    const out = {};
    for (const [k, v] of Object.entries(value)) {
      try {
        out[String(k)] = jsonable(v);
      } catch (_) {
        out[String(k)] = safeRepr(v, 200);
      }
    }
    return out;
  }
  if (t === 'function') return `<function ${value.name || 'anonymous'}>`;
  return safeRepr(value);
}

function printHeader(title) {
  const line = '='.repeat(78);
  console.log(`\n${line}\n${title}\n${line}`);
}

function printKv(key, value) {
  const k = String(key).padEnd(34, ' ');
  console.log(`${k}: ${value}`);
}

function parseArgs(argv) {
  const args = {
    install: false,
    package: 'sst-core@0.8.18',
    jsonOut: '',
    csvOut: '',
    quiet: false,
    runBindingTests: false,
    regenManifest: false,
    strictBindings: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--install') args.install = true;
    else if (a === '--package') args.package = argv[++i] || args.package;
    else if (a === '--json-out') args.jsonOut = argv[++i] || '';
    else if (a === '--csv-out') args.csvOut = argv[++i] || '';
    else if (a === '--quiet') args.quiet = true;
    else if (a === '--run-binding-tests') args.runBindingTests = true;
    else if (a === '--regen-manifest') args.regenManifest = true;
    else if (a === '--strict-bindings') args.strictBindings = true;
    else if (a === '--help' || a === '-h') {
      console.log(`Usage: node SSTcore_full_probe.js [options]

Options:
  --install              npm install --package before probing
  --package <spec>       npm package spec (default: sst-core@0.8.18)
  --json-out <path>      write JSON report
  --csv-out <prefix>     write CSV tables (prefix or directory)
  --quiet                suppress summary printing
  --run-binding-tests    run npm test
  --regen-manifest       skipped on Node (Python tooling)
  --strict-bindings      exit 2 if binding catalog checks fail
`);
      process.exit(0);
    }
  }
  return args;
}

function runNpmInstall(packageSpec) {
  const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  const completed = spawnSync(cmd, ['install', packageSpec], {
    encoding: 'utf8',
    cwd: PROBE_ROOT,
    shell: process.platform === 'win32',
  });
  return {
    cmd: [cmd, 'install', packageSpec],
    returncode: completed.status,
    stdout_tail: (completed.stdout || '').slice(-4000),
    stderr_tail: (completed.stderr || '').slice(-4000),
  };
}

function runNpmTest() {
  const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  const completed = spawnSync(cmd, ['test'], {
    encoding: 'utf8',
    cwd: PROBE_ROOT,
    shell: process.platform === 'win32',
  });
  const out = `${completed.stdout || ''}\n${completed.stderr || ''}`;
  return {
    attempted: true,
    skipped: false,
    ok: completed.status === 0,
    exit_code: completed.status,
    summary_line: out.trim().split(/\r?\n/).slice(-5).join(' | '),
    stdout_tail: (completed.stdout || '').slice(-4000),
    stderr_tail: (completed.stderr || '').slice(-4000),
  };
}

// ---------------------------------------------------------------------
// Load SSTcore
// ---------------------------------------------------------------------

function loadSstcore() {
  const info = {
    attempts: [],
    selected_import_name: null,
    import_ok: false,
    error: null,
  };

  const candidates = [
    { name: './index.js', resolve: () => path.join(PROBE_ROOT, 'index.js') },
    { name: 'sst-core', resolve: () => 'sst-core' },
    { name: 'SSTcore', resolve: () => 'SSTcore' },
  ];

  for (const c of candidates) {
    const id = c.resolve();
    try {
      if (c.name === './index.js' && !fs.existsSync(id)) {
        info.attempts.push({ name: c.name, ok: false, error: 'file missing' });
        continue;
      }
      const mod = require(id);
      info.attempts.push({ name: c.name, ok: true, error: null });
      info.selected_import_name = c.name;
      info.import_ok = true;
      return { sst: mod, info };
    } catch (exc) {
      info.attempts.push({
        name: c.name,
        ok: false,
        error: `${exc && exc.name}: ${exc && exc.message}`,
      });
    }
  }

  info.error = 'all import attempts failed';
  return { sst: null, info };
}

// ---------------------------------------------------------------------
// Probe sections
// ---------------------------------------------------------------------

function probeEnvironment() {
  return {
    timestamp_utc: nowIso(),
    node_executable: process.execPath,
    node_version: process.version,
    platform: process.platform,
    arch: process.arch,
    os_release: os.release(),
    cwd: process.cwd(),
    probe_root: PROBE_ROOT,
    env_SSTCORE_RESOURCES: process.env.SSTCORE_RESOURCES || null,
  };
}

function probeModule(sst, importInfo) {
  let pkgVersion = null;
  try {
    const pkg = JSON.parse(fs.readFileSync(path.join(PROBE_ROOT, 'package.json'), 'utf8'));
    pkgVersion = pkg.version;
  } catch (_) { /* optional */ }

  return {
    import_info: importInfo,
    module_file: path.join(PROBE_ROOT, 'index.js'),
    version: sst.version || sst.engineVersion || pkgVersion || 'unknown',
    isAvailable: !!sst.isAvailable,
    isNative: !!sst.isNative,
    isWasm: !!sst.isWasm,
    nativeAddonName: sst.nativeAddonName || null,
    error: sst.error || null,
  };
}

function probePublicApi(sst) {
  const rows = [];
  const names = Object.keys(sst).sort();
  for (const name of names) {
    if (name.startsWith('_')) continue;
    try {
      const obj = sst[name];
      let kind = typeof obj;
      if (kind === 'function') {
        kind = /^[A-Z]/.test(name) ? 'class' : 'function';
      }
      rows.push({
        name,
        kind,
        signature: '',
        doc_first_line: '',
      });
    } catch (exc) {
      rows.push({
        name,
        kind: 'ERROR',
        signature: '',
        doc_first_line: `${exc && exc.name}: ${exc && exc.message}`,
      });
    }
  }
  return rows;
}

/** Only these may be invoked with zero args during the helper probe (N-API wrappers often report .length===0). */
const SAFE_NOARG_HELPERS = new Set([
  'engineInfo',
  'getCapabilities',
  'listBindings',
  'get_resources_dir',
  'get_ideal_txt_path',
  'get_knots_fourier_series_dir',
  'get_knotplot_dir',
  'list_ideal_source_files',
  'list_embedded_fseries_ids',
]);

function summarizeHelperSample(name, value) {
  if (value == null) return { kind: 'null' };
  if (typeof value === 'string') {
    return { kind: 'string', length: value.length, preview: value.slice(0, 80) };
  }
  if (Array.isArray(value)) {
    return { kind: 'array', count: value.length, sample: value.slice(0, 8) };
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value);
    const out = { kind: 'object', keys: keys.slice(0, 12) };
    if (name === 'resolve_knot_ref') {
      out.ref = value.ref;
      out.source = value.source;
      out.role = value.role;
      out.ropelength = value.ropelength;
      out.canonicalAbId = value.canonicalAbId;
      out.hasIdealXml = !!value.idealXml;
      out.idealXmlLength = value.idealXml ? String(value.idealXml).length : 0;
    }
    if (name === 'list_ideal_source_files') {
      out.count = keys.length;
    }
    return out;
  }
  return { kind: typeof value, preview: safeRepr(value, 80) };
}

function summarizeEmbeddedValue(value) {
  if (value == null) return { empty: true };
  if (Array.isArray(value)) {
    return {
      kind: 'array',
      count: value.length,
      sample: value.slice(0, 20).map((x) => (typeof x === 'string' ? x.slice(0, 80) : safeRepr(x, 80))),
    };
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value);
    return {
      kind: 'object',
      count: keys.length,
      sample_keys: keys.slice(0, 20),
    };
  }
  return { kind: typeof value, preview: safeRepr(value, 120) };
}

function probeExpectedHelpers(sst) {
  const rows = [];
  for (const name of EXPECTED_NODE_HELPERS) {
    const exists = name in sst && sst[name] != null;
    const obj = exists ? sst[name] : null;
    const row = {
      name,
      exists,
      callable: exists && typeof obj === 'function',
      call_ok: null,
      value: null,
      error: null,
    };
    if (row.callable && SAFE_NOARG_HELPERS.has(name)) {
      try {
        const value = obj();
        row.call_ok = true;
        if (name === 'list_embedded_fseries_ids' || name === 'list_ideal_source_files') {
          row.value = summarizeHelperSample(name, value);
        } else if (
          name === 'get_resources_dir' ||
          name === 'get_ideal_txt_path' ||
          name === 'get_knots_fourier_series_dir' ||
          name === 'get_knotplot_dir'
        ) {
          row.value = value == null ? null : String(value);
        } else {
          row.value = jsonable(value);
        }
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && (name === 'getEmbeddedKnotFiles' || name === 'getEmbeddedIdealFiles')) {
      try {
        row.call_ok = true;
        row.value = summarizeEmbeddedValue(obj());
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && name === 'get_ideal_ab') {
      try {
        row.call_ok = true;
        row.value = summarizeHelperSample(name, obj('3:1:1'));
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && name === 'get_ideal_link') {
      try {
        row.call_ok = true;
        row.value = summarizeHelperSample(name, obj('L2a1'));
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && name === 'load_fseries_knot') {
      try {
        row.call_ok = true;
        row.value = summarizeHelperSample(name, obj('3_1'));
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && name === 'resolve_knot_ref') {
      try {
        row.call_ok = true;
        row.value = summarizeHelperSample(name, obj('3:1:1'));
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    } else if (row.callable && name === 'knotplot') {
      try {
        row.call_ok = true;
        row.value = summarizeHelperSample(name, obj('knot_3.1'));
      } catch (exc) {
        row.call_ok = false;
        row.error = `${exc && exc.name}: ${exc && exc.message}`;
      }
    }
    rows.push(row);
  }
  for (const name of PYTHON_ONLY_HELPERS) {
    rows.push({
      name,
      exists: false,
      callable: false,
      call_ok: null,
      value: null,
      error: 'python-only helper (not on Node surface)',
    });
  }
  return rows;
}

function probeResources(sst) {
  const result = {
    mode: 'embedded_napi',
    embedded_knot_files: null,
    embedded_knot_count: null,
    embedded_ideal_files: null,
    embedded_ideal_count: null,
    repo_resources_dir: null,
    repo_resources_exists: false,
    errors: [],
  };

  try {
    if (typeof sst.getEmbeddedKnotFiles === 'function') {
      const summary = summarizeEmbeddedValue(sst.getEmbeddedKnotFiles());
      result.embedded_knot_files = summary;
      result.embedded_knot_count = summary.count != null ? summary.count : null;
    }
  } catch (exc) {
    result.errors.push(`getEmbeddedKnotFiles: ${exc && exc.name}: ${exc && exc.message}`);
  }

  try {
    if (typeof sst.getEmbeddedIdealFiles === 'function') {
      const summary = summarizeEmbeddedValue(sst.getEmbeddedIdealFiles());
      result.embedded_ideal_files = summary;
      result.embedded_ideal_count = summary.count != null ? summary.count : null;
    }
  } catch (exc) {
    result.errors.push(`getEmbeddedIdealFiles: ${exc && exc.name}: ${exc && exc.message}`);
  }

  const resDir = path.join(PROBE_ROOT, 'resources');
  result.repo_resources_dir = resDir;
  result.repo_resources_exists = fs.existsSync(resDir);
  if (result.repo_resources_exists) {
    try {
      result.repo_resources_entries = fs.readdirSync(resDir).slice(0, 100);
    } catch (exc) {
      result.errors.push(`readdir resources: ${exc && exc.message}`);
    }
  }
  return result;
}

function summarizeJsCatalog(catalog, sampleIds, catalogPath) {
  const summary = {
    load_ok: false,
    source: catalog && catalog.source != null ? catalog.source : null,
    path: catalogPath || null,
    id_count: 0,
    sample_hits: [],
    error: null,
  };
  try {
    if (!catalog || !Array.isArray(catalog.ids) || !catalog.db || typeof catalog.db !== 'object') {
      summary.error = 'catalog missing ids/db';
      return summary;
    }
    summary.id_count = catalog.ids.length;
    for (const id of sampleIds) {
      const entry = catalog.db[id];
      const present = entry != null && typeof entry === 'object';
      const hit = {
        id,
        present,
        component_count: present && Array.isArray(entry.components) ? entry.components.length : 0,
        L: present && entry.L != null ? entry.L : null,
        D: present && entry.D != null ? entry.D : null,
        label: present ? entry.label || entry.knotId || null : null,
        family: present && entry.family != null ? entry.family : null,
        status: present && entry.status != null ? entry.status : null,
      };
      summary.sample_hits.push(hit);
    }
    const samplesOk =
      summary.id_count > 0 &&
      summary.sample_hits.length > 0 &&
      summary.sample_hits.every((h) => h.present && h.component_count >= 1);
    summary.load_ok = samplesOk;
    if (!samplesOk && !summary.error) {
      const missing = summary.sample_hits.filter((h) => !h.present || h.component_count < 1).map((h) => h.id);
      summary.error = missing.length ? `sample lookup failed: ${missing.join(', ')}` : 'empty catalog';
    }
  } catch (exc) {
    summary.error = `${exc && exc.name}: ${exc && exc.message}`;
  }
  return summary;
}

function probeJsCatalog(loaderFn, sourceKey, sampleIds) {
  const paths = catalogPaths();
  const catalogPath = paths[sourceKey] || null;
  try {
    const catalog = loaderFn();
    return summarizeJsCatalog(catalog, sampleIds, catalogPath);
  } catch (exc) {
    return {
      load_ok: false,
      source: sourceKey,
      path: catalogPath,
      id_count: 0,
      sample_hits: [],
      error: `${exc && exc.name}: ${exc && exc.message}`,
    };
  }
}

function probeIdealCatalog(sst) {
  const result = {
    catalog_ok: false,
    sources: [],
    present_count: 0,
    lookup_ok_count: 0,
    js_catalog: null,
    errors: [],
  };

  result.js_catalog = probeJsCatalog(loadIdealCatalog, 'ideal', ['3:1:1', '4:1:1', 'L2a1']);
  if (!result.js_catalog.load_ok && result.js_catalog.error) {
    result.errors.push(`js_catalog: ${result.js_catalog.error}`);
  }

  if (typeof sst.getEmbeddedIdealFiles !== 'function') {
    result.errors.push('getEmbeddedIdealFiles is not available');
    result.catalog_ok = false;
    return result;
  }

  let files = [];
  try {
    files = sst.getEmbeddedIdealFiles() || [];
  } catch (exc) {
    result.errors.push(`${exc && exc.name}: ${exc && exc.message}`);
    result.catalog_ok = false;
    return result;
  }

  result.present_count = Array.isArray(files) ? files.length : Object.keys(files || {}).length;

  const samples = [
    { id: '3:1:1', label: 'trefoil' },
    { id: '4:1:1', label: 'figure_eight' },
    { id: 'L2a1', label: 'hopf_link' },
  ];

  for (const sample of samples) {
    const row = {
      sample_id: sample.id,
      label: sample.label,
      lookup_ok: null,
      lookup_error: null,
      preview: null,
    };
    const { ok, error, summary } = tryTopologyLookup(sst, sample.id.startsWith('L') ? 'LINK' : 'AB', sample.id);
    row.lookup_ok = ok;
    row.lookup_error = error;
    row.preview = summary && summary.raw_preview;
    if (row.lookup_ok) result.lookup_ok_count += 1;
    result.sources.push(row);
  }

  const nativeOk = result.present_count > 0 && result.lookup_ok_count > 0;
  result.catalog_ok = nativeOk && !!result.js_catalog.load_ok;
  return result;
}

function probeKnotsFourierSeriesCatalog(sst) {
  const result = {
    catalog_ok: false,
    fseries_count: null,
    probe_labels: [],
    js_catalog: null,
    errors: [],
  };

  result.js_catalog = probeJsCatalog(loadFseriesCatalog, 'fseries', ['3_1', '4_1', '5_2']);
  if (!result.js_catalog.load_ok && result.js_catalog.error) {
    result.errors.push(`js_catalog: ${result.js_catalog.error}`);
  }

  try {
    if (typeof sst.getEmbeddedKnotFiles === 'function') {
      const files = sst.getEmbeddedKnotFiles() || [];
      result.fseries_count = Array.isArray(files) ? files.length : Object.keys(files || {}).length;
    }
  } catch (exc) {
    result.errors.push(`${exc && exc.name}: ${exc && exc.message}`);
  }

  for (const label of FSERIES_PROBE_LABELS) {
    const row = {
      label,
      load_ok: null,
      parse_ok: null,
      error: null,
    };
    try {
      if (typeof sst.loadKnot === 'function') {
        const loaded = sst.loadKnot(label);
        row.load_ok = loaded != null;
        row.preview = safeRepr(loaded, 160);
      } else {
        row.load_ok = false;
        row.error = 'loadKnot not available';
      }
      if (typeof sst.parseFseriesFromString === 'function' && typeof sst.loadEmbeddedKnotBlock === 'function') {
        try {
          const block = sst.loadEmbeddedKnotBlock(label);
          if (block) {
            row.parse_ok = true;
          }
        } catch (_) {
          /* optional path */
        }
      }
    } catch (exc) {
      row.load_ok = false;
      row.error = `${exc && exc.name}: ${exc && exc.message}`;
    }
    result.probe_labels.push(row);
  }

  const nativeOk =
    (result.fseries_count || 0) > 0 && result.probe_labels.some((r) => r.load_ok);
  result.catalog_ok = nativeOk && !!result.js_catalog.load_ok;
  return result;
}

function probeKnotplotCatalog() {
  const result = {
    catalog_ok: false,
    skipped: false,
    js_catalog: null,
    errors: [],
  };
  result.js_catalog = probeJsCatalog(loadKnotplotCatalog, 'knotplot', ['knot_3.1', 'torus_6.9']);
  if (!result.js_catalog.load_ok && result.js_catalog.error) {
    result.errors.push(`js_catalog: ${result.js_catalog.error}`);
  }
  result.catalog_ok = !!result.js_catalog.load_ok;
  return result;
}

function probeBindingCatalog(sst) {
  const result = {
    list_bindings_ok: false,
    counts: null,
    sample_functions: [],
    sample_classes: [],
    errors: [],
    skipped_python_manifest: true,
    skip_reason: 'binding_manifest / binding_inventory are Python tooling',
  };
  try {
    if (typeof sst.listBindings !== 'function') {
      result.errors.push('listBindings missing');
      return result;
    }
    const lb = sst.listBindings();
    result.list_bindings_ok = true;
    result.counts = lb.counts || null;
    result.sample_functions = (lb.functions || []).slice(0, 30);
    result.sample_classes = (lb.classes || []).slice(0, 30);
  } catch (exc) {
    result.errors.push(`${exc && exc.name}: ${exc && exc.message}`);
  }
  return result;
}

function probeExamplesCoverage() {
  const result = {
    modules_expected: null,
    example_ts_files: 0,
    example_py_files: 0,
    present_ts: [],
    missing_vs_node_binds: [],
    errors: [],
  };
  const examplesDir = path.join(PROBE_ROOT, 'examples');
  const srcDir = path.join(PROBE_ROOT, 'src');
  if (!fs.existsSync(examplesDir)) {
    result.errors.push(`examples missing: ${examplesDir}`);
    return result;
  }
  const ts = fs.readdirSync(examplesDir).filter((f) => f.startsWith('example_') && f.endsWith('.ts'));
  const py = fs.readdirSync(examplesDir).filter((f) => f.startsWith('example_') && f.endsWith('.py'));
  result.example_ts_files = ts.length;
  result.example_py_files = py.length;
  result.present_ts = ts.sort();

  if (fs.existsSync(srcDir)) {
    const nodeBinds = fs
      .readdirSync(srcDir)
      .filter((f) => f.endsWith('_node.cpp') && f !== 'module_node.cpp')
      .map((f) => f.replace(/_node\.cpp$/, ''));
    result.modules_expected = nodeBinds.length;
    // Heuristic: example_<stem>.ts where stem loosely matches
    for (const stem of nodeBinds) {
      const candidates = [
        `example_${stem}.ts`,
        `example_${stem.replace(/_mass$/, '')}.ts`,
        `example_${stem.replace(/_dynamics$/, '_rotation')}.ts`,
      ];
      // known renames
      const special = {
        fluid_dynamics: 'example_fluid_rotation.ts',
        potential_timefield: 'example_potential_flow.ts',
        vorticity_dynamics: 'example_vorticity_transport.ts',
        ab_initio_mass: 'example_ab_initio.ts',
        knot_dynamics: 'example_knot.ts',
        hyperbolic_volume: 'example_hyperbolic_volume.ts',
      };
      if (special[stem]) candidates.unshift(special[stem]);
      if (!candidates.some((c) => ts.includes(c))) {
        // tube geometry_node is under src/tube
        if (stem !== 'geometry') result.missing_vs_node_binds.push(stem);
      }
    }
  }
  result.coverage_ok = (result.missing_vs_node_binds || []).length === 0;
  return result;
}

function probeNativeBindings(sst) {
  const result = {
    native_found: !!sst.isNative,
    wasm_found: !!sst.isWasm,
    available: !!sst.isAvailable,
    native_addon_name: sst.nativeAddonName || null,
    engine_info: null,
    capabilities: null,
    list_bindings_result: null,
    errors: [],
  };
  try {
    if (typeof sst.engineInfo === 'function') result.engine_info = jsonable(sst.engineInfo());
  } catch (exc) {
    result.errors.push(`engineInfo: ${exc && exc.message}`);
  }
  try {
    if (typeof sst.getCapabilities === 'function') result.capabilities = jsonable(sst.getCapabilities());
  } catch (exc) {
    result.errors.push(`getCapabilities: ${exc && exc.message}`);
  }
  try {
    if (typeof sst.listBindings === 'function') {
      const lb = sst.listBindings();
      result.list_bindings_result = {
        counts: lb.counts,
        functions_sample: (lb.functions || []).slice(0, 40),
        classes_sample: (lb.classes || []).slice(0, 40),
      };
    }
  } catch (exc) {
    result.errors.push(`listBindings: ${exc && exc.message}`);
  }
  return result;
}

function tryTopologyLookup(sst, kind, topologyId) {
  // Some IDs (e.g. 5:2:1) can abort the native addon; always probe in a child.
  const script = `
    const sst = require('./index.js');
    const kind = ${JSON.stringify(kind)};
    const id = ${JSON.stringify(topologyId)};
    try {
      let value = null;
      if (kind === 'AB') {
        if (typeof sst.parseEmbeddedIdealAbById === 'function') value = sst.parseEmbeddedIdealAbById(id);
        else if (typeof sst.findIdealAbBlockById === 'function') value = sst.findIdealAbBlockById(id);
        else { console.log(JSON.stringify({ok:false,error:'no AB lookup'})); process.exit(0); }
      } else if (kind === 'LINK') {
        if (typeof sst.findIdealBlockById === 'function') value = sst.findIdealBlockById(id);
        else if (typeof sst.parseEmbeddedIdealAbById === 'function') value = sst.parseEmbeddedIdealAbById(id);
        else { console.log(JSON.stringify({ok:false,error:'no LINK lookup'})); process.exit(0); }
      } else {
        console.log(JSON.stringify({ok:false,error:'unknown kind'}));
        process.exit(0);
      }
      const summary = {
        ok: true,
        error: null,
        raw_type: value==null ? String(value) : typeof value,
        is_empty: value==null || value==='' || (Array.isArray(value)&&value.length===0),
        keys: value && typeof value==='object' && !Array.isArray(value) ? Object.keys(value).slice(0,30) : null,
        length_like: null,
      };
      if (summary.keys) {
        for (const k of ['L','length','ropelength','L_total','total_length','ropelengthTotal']) {
          if (k in value) { summary.length_like = value[k]; break; }
        }
      }
      console.log(JSON.stringify(summary));
    } catch (e) {
      console.log(JSON.stringify({ok:false,error:(e&&e.name)+': '+(e&&e.message)}));
    }
  `;
  const child = spawnSync(process.execPath, ['-e', script], {
    encoding: 'utf8',
    cwd: PROBE_ROOT,
    timeout: 30000,
  });
  if (child.status !== 0) {
    return {
      ok: false,
      value: null,
      error: `native abort status=${child.status} signal=${child.signal}`,
      summary: {
        raw_type: 'aborted',
        raw_preview: '',
        is_empty: true,
        length_like: null,
        keys: null,
      },
    };
  }
  try {
    const line = (child.stdout || '').trim().split(/\r?\n/).filter(Boolean).pop();
    const parsed = JSON.parse(line);
    return {
      ok: !!parsed.ok,
      value: parsed,
      error: parsed.error || null,
      summary: {
        raw_type: parsed.raw_type || typeof parsed,
        raw_preview: safeRepr(parsed, 400),
        is_empty: !!parsed.is_empty,
        length_like: parsed.length_like != null ? parsed.length_like : null,
        keys: parsed.keys || null,
      },
    };
  } catch (exc) {
    return {
      ok: false,
      value: null,
      error: `parse child output: ${exc && exc.message}`,
      summary: { raw_type: 'error', raw_preview: (child.stdout || '').slice(0, 200), is_empty: true, length_like: null, keys: null },
    };
  }
}

function probeTopologies(sst) {
  const rows = [];
  for (const [label, kind, topologyId] of TOPOLOGY_CANDIDATES) {
    const { ok, error, summary } = tryTopologyLookup(sst, kind, topologyId);
    rows.push({
      label,
      kind,
      topology_id: topologyId,
      lookup_call_ok: ok,
      found_nonempty: ok && summary && !summary.is_empty,
      error,
      ...summary,
    });
  }
  return rows;
}

function computeConstantChecks() {
  const c = SST_CONSTANTS.c_m_s;
  const v = SST_CONSTANTS.v_swirl_m_s;
  const r_c = SST_CONSTANTS.r_c_m;
  const rho_f = SST_CONSTANTS.rho_f_kg_m3;
  const rho_core = SST_CONSTANTS.rho_core_kg_m3;
  const rho_E = SST_CONSTANTS.rho_E_J_m3;
  const joule_per_MeV = SST_CONSTANTS.joule_per_MeV;

  const omega_c = v / r_c;
  const Gamma_0 = 2.0 * Math.PI * r_c * v;
  const alpha_swirl = (2.0 * v) / c;

  const E_core_J = Math.PI * rho_E * r_c ** 3;
  const E_core_MeV = E_core_J / joule_per_MeV;
  const E_meson0_J = alpha_swirl * E_core_J;
  const E_meson0_MeV = E_meson0_J / joule_per_MeV;

  const ambient_energy_density = 0.5 * rho_f * v ** 2;
  const swirl_clock_c = Math.sqrt(1.0 - (v / c) ** 2);

  return {
    inputs: SST_CONSTANTS,
    omega_c_s_inv: omega_c,
    Gamma_0_m2_s: Gamma_0,
    alpha_swirl,
    E_core_J,
    E_core_MeV,
    E_meson0_J,
    E_meson0_MeV,
    ambient_energy_density_J_m3: ambient_energy_density,
    ambient_to_core_energy_density_ratio: ambient_energy_density / rho_E,
    condensation_ratio_rho_core_over_rho_f: rho_core / rho_f,
    swirl_clock_using_c: swirl_clock_c,
    swirl_clock_using_c_inverse_square: 1.0 / swirl_clock_c ** 2,
  };
}

function linkedCarrierScaffold(nComponents, linkingNumber, lambdaLink, chiralityBindingMeV, dressingMeV, E0MeV) {
  return (nComponents + lambdaLink * Math.abs(linkingNumber)) * E0MeV - chiralityBindingMeV + dressingMeV;
}

function computeMesonLinkScaffolds(E0MeV) {
  const rows = [];
  for (const [name, lk] of [
    ['open_single_anchor', 0],
    ['hopf_link', 1],
    ['solomon_link', 2],
  ]) {
    for (const lambda_link of [0.0, 0.25, 0.5, 1.0]) {
      const n_components = name === 'open_single_anchor' ? 1 : 2;
      rows.push({
        candidate: name,
        n_components,
        linking_number: lk,
        lambda_link,
        chirality_binding_MeV: 0.0,
        dressing_MeV: 0.0,
        energy_MeV: linkedCarrierScaffold(n_components, lk, lambda_link, 0.0, 0.0, E0MeV),
      });
    }
  }
  return rows;
}

function probeParticleEvaluator(sst) {
  const result = {
    particle_evaluator_exists: typeof sst.ParticleEvaluator === 'function',
    trefoil_canon_ok: null,
    trefoil_canon_error: null,
    knotplot_reject_ok: null,
    knotplot_reject_error: null,
    resolve_knot_ref_ok: null,
    resolve_knot_ref_error: 'resolve_knot_ref is Python-only',
    errors: [],
  };
  if (!result.particle_evaluator_exists) {
    result.errors.push('ParticleEvaluator not exported');
    return result;
  }
  try {
    // eslint-disable-next-line no-new
    new sst.ParticleEvaluator('3:1:1', 200);
    result.trefoil_canon_ok = true;
  } catch (exc) {
    result.trefoil_canon_ok = false;
    result.trefoil_canon_error = `${exc && exc.name}: ${exc && exc.message}`;
  }

  // Non-canon id may abort the native addon (not a JS exception). Probe in a subprocess.
  const child = spawnSync(
    process.execPath,
    [
      '-e',
      "const sst=require('./index.js'); try { new sst.ParticleEvaluator('knot_3.1', 50); console.log('UNEXPECTED_OK'); } catch(e){ console.log('REJECTED:'+(e&&e.message)); }",
    ],
    { encoding: 'utf8', cwd: PROBE_ROOT, timeout: 30000, shell: false },
  );
  if (child.status === 0 && /REJECTED:/.test(child.stdout || '')) {
    result.knotplot_reject_ok = true;
    result.knotplot_reject_error = (child.stdout || '').trim();
  } else if (child.status === 0 && /UNEXPECTED_OK/.test(child.stdout || '')) {
    result.knotplot_reject_ok = false;
    result.knotplot_reject_error = 'expected rejection for non-canon id';
  } else {
    result.knotplot_reject_ok = true;
    result.knotplot_reject_error = `native abort or non-zero exit (status=${child.status}, signal=${child.signal})`;
  }
  return result;
}

function tryExportTrefoilCurve(sst, channel, ref) {
  const out = {
    curve_export_ok: false,
    curve_export_error: null,
    sample_count: 0,
    computed_length: null,
  };
  try {
    if (typeof sst.loadKnot === 'function' && channel !== 'ideal_txt') {
      const loaded = sst.loadKnot(ref);
      if (loaded && loaded.points) {
        out.sample_count = loaded.points.length || 0;
        out.curve_export_ok = out.sample_count > 0;
        return out;
      }
    }
    if (typeof sst.evaluateFourierBlock === 'function' && typeof sst.parseEmbeddedIdealAbById === 'function' && channel === 'ideal_txt') {
      const block = sst.parseEmbeddedIdealAbById(ref);
      if (!block) {
        out.curve_export_error = 'parseEmbeddedIdealAbById returned empty';
        return out;
      }
      // Some wrappers return structured objects; try lengthExact on largest block if available
      if (typeof sst.lengthExact === 'function') {
        try {
          out.computed_length = sst.lengthExact(block, TREFOIL_EXPORT_SAMPLES);
          out.curve_export_ok = true;
        } catch (exc) {
          out.curve_export_error = `${exc && exc.name}: ${exc && exc.message}`;
        }
      } else {
        out.curve_export_ok = block != null;
      }
      return out;
    }
    if (typeof sst.loadKnot === 'function') {
      const loaded = sst.loadKnot(ref.includes(':') ? '3_1' : ref);
      out.curve_export_ok = loaded != null;
      out.sample_count = loaded && loaded.points ? loaded.points.length : 0;
      return out;
    }
    out.curve_export_error = 'no suitable curve export path';
  } catch (exc) {
    out.curve_export_error = `${exc && exc.name}: ${exc && exc.message}`;
  }
  return out;
}

function probeTrefoilTriad(sst) {
  const result = {
    channels: [],
    catalog_ok: true,
    canon_ropelength: CANON_TREFOIL_ROPELENGTH,
    resolve_knot_ref_available: false,
    note: 'Node triad uses ParticleEvaluator + embedded/loadKnot (no resolve_knot_ref)',
  };

  for (const spec of TREFOIL_TRIAD_CHANNELS) {
    const row = {
      channel: spec.channel,
      ref: spec.ref,
      source: spec.source,
      resolve_ok: false,
      particle_evaluator: 'skipped',
      particle_evaluator_error: null,
      ropelength_delta_vs_canon: null,
      error: null,
    };

    if (spec.expect_particle_evaluator !== 'skip' && typeof sst.ParticleEvaluator === 'function') {
      if (spec.expect_particle_evaluator === 'reject') {
        const child = spawnSync(
          process.execPath,
          [
            '-e',
            `const sst=require('./index.js'); try { new sst.ParticleEvaluator(${JSON.stringify(spec.ref)}, 50); console.log('OK'); } catch(e){ console.log('REJ'); }`,
          ],
          { encoding: 'utf8', cwd: PROBE_ROOT, timeout: 30000 },
        );
        if (child.status === 0 && /REJ/.test(child.stdout || '')) {
          row.particle_evaluator = 'rejected';
        } else if (child.status === 0 && /OK/.test(child.stdout || '')) {
          row.particle_evaluator = 'ok';
        } else {
          row.particle_evaluator = 'rejected';
          row.particle_evaluator_error = `native abort status=${child.status}`;
        }
        row.resolve_ok = true;
      } else {
        try {
          // eslint-disable-next-line no-new
          new sst.ParticleEvaluator(spec.ref, 200);
          row.particle_evaluator = 'ok';
          row.resolve_ok = true;
        } catch (exc) {
          row.particle_evaluator = 'rejected';
          row.particle_evaluator_error = `${exc && exc.name}: ${exc && exc.message}`;
        }
      }
      if (spec.expect_particle_evaluator === 'ok' && row.particle_evaluator !== 'ok') result.catalog_ok = false;
      if (spec.expect_particle_evaluator === 'reject' && row.particle_evaluator === 'ok') result.catalog_ok = false;
    } else if (spec.expect_particle_evaluator === 'skip') {
      row.particle_evaluator = 'skipped';
      row.resolve_ok = true;
    }

    Object.assign(row, tryExportTrefoilCurve(sst, spec.channel, spec.ref));
    result.channels.push(row);
  }
  return result;
}

function writeCsv(filePath, rows) {
  if (!rows || !rows.length) {
    fs.writeFileSync(filePath, '', 'utf8');
    return;
  }
  const keys = [];
  for (const row of rows) {
    for (const k of Object.keys(row)) {
      if (!keys.includes(k)) keys.push(k);
    }
  }
  const escape = (v) => {
    const s = String(v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : v);
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  };
  const lines = [keys.join(',')];
  for (const row of rows) {
    lines.push(keys.map((k) => escape(jsonable(row[k]))).join(','));
  }
  fs.writeFileSync(filePath, `${lines.join('\n')}\n`, 'utf8');
}

function makeReport(sst, importInfo, opts = {}) {
  const report = {
    environment: probeEnvironment(),
    module: probeModule(sst, importInfo),
    public_api: probePublicApi(sst),
    expected_helpers: probeExpectedHelpers(sst),
    resources: probeResources(sst),
    ideal_catalog: probeIdealCatalog(sst),
    knots_fourier_series_catalog: probeKnotsFourierSeriesCatalog(sst),
    knotplot_catalog: probeKnotplotCatalog(),
    binding_catalog: probeBindingCatalog(sst),
    examples_coverage: probeExamplesCoverage(),
    native_bindings: probeNativeBindings(sst),
    topology_candidates: probeTopologies(sst),
    particle_evaluator: probeParticleEvaluator(sst),
    trefoil_triad: probeTrefoilTriad(sst),
    constant_checks: computeConstantChecks(),
  };
  report.meson_link_scaffolds = computeMesonLinkScaffolds(report.constant_checks.E_meson0_MeV);
  if (opts.runBindingTests) {
    report.binding_tests = runNpmTest();
  }
  if (opts.regenManifest) {
    report.manifest_regen = {
      skipped: true,
      skip_reason: 'manifest regeneration is Python tooling (scripts/gen_binding_manifest.py)',
    };
  }
  return report;
}

function printReportSummary(report) {
  printHeader('Environment');
  const env = report.environment;
  printKv('timestamp_utc', env.timestamp_utc);
  printKv('node_executable', env.node_executable);
  printKv('node_version', env.node_version);
  printKv('platform', `${env.platform}/${env.arch}`);
  printKv('cwd', env.cwd);

  printHeader('SSTcore module (Node)');
  const module = report.module;
  printKv('import_ok', module.import_info.import_ok);
  printKv('selected_import_name', module.import_info.selected_import_name);
  printKv('version', module.version);
  printKv('isNative', module.isNative);
  printKv('isWasm', module.isWasm);
  printKv('isAvailable', module.isAvailable);

  printHeader('Expected helpers');
  for (const row of report.expected_helpers) {
    console.log(
      `${String(row.name).padEnd(34)} exists=${String(row.exists).padEnd(5)} ` +
        `callable=${String(row.callable).padEnd(5)} ` +
        `call_ok=${String(row.call_ok).padEnd(5)} ` +
        `error=${row.error}`,
    );
  }

  printHeader('Resources (embedded)');
  const res = report.resources;
  printKv('embedded_knot_count', res.embedded_knot_count);
  printKv('embedded_ideal_count', res.embedded_ideal_count);
  printKv('repo_resources_exists', res.repo_resources_exists);
  if (res.errors && res.errors.length) {
    console.log('Resource errors:');
    for (const err of res.errors) console.log('  -', err);
  }

  printHeader('Ideal catalog (embedded + JS)');
  const ideal = report.ideal_catalog || {};
  printKv('catalog_ok', ideal.catalog_ok);
  printKv('present_count', ideal.present_count);
  printKv('lookup_ok_count', ideal.lookup_ok_count);
  const idealJs = ideal.js_catalog || {};
  printKv('js_load_ok', idealJs.load_ok);
  printKv('js_id_count', idealJs.id_count);
  printKv('js_path', idealJs.path);
  for (const hit of idealJs.sample_hits || []) {
    console.log(
      `  js ${String(hit.id).padEnd(10)} present=${String(hit.present).padEnd(5)} ` +
        `components=${hit.component_count} L=${hit.L} label=${hit.label}`,
    );
  }
  for (const row of ideal.sources || []) {
    console.log(
      `${String(row.label).padEnd(18)} ${String(row.sample_id).padEnd(10)} ` +
        `lookup_ok=${String(row.lookup_ok).padEnd(5)} error=${row.lookup_error}`,
    );
  }
  if (ideal.errors && ideal.errors.length) {
    for (const err of ideal.errors) console.log('  -', err);
  }

  printHeader('Knots_FourierSeries catalog (embedded + JS)');
  const kfs = report.knots_fourier_series_catalog || {};
  printKv('catalog_ok', kfs.catalog_ok);
  printKv('fseries_count', kfs.fseries_count);
  const kfsJs = kfs.js_catalog || {};
  printKv('js_load_ok', kfsJs.load_ok);
  printKv('js_id_count', kfsJs.id_count);
  for (const hit of kfsJs.sample_hits || []) {
    console.log(
      `  js ${String(hit.id).padEnd(8)} present=${String(hit.present).padEnd(5)} components=${hit.component_count}`,
    );
  }
  for (const row of kfs.probe_labels || []) {
    console.log(
      `${String(row.label).padEnd(8)} load_ok=${String(row.load_ok).padEnd(5)} error=${row.error}`,
    );
  }
  if (kfs.errors && kfs.errors.length) {
    for (const err of kfs.errors) console.log('  -', err);
  }

  printHeader('knotplot catalog (JS)');
  const kp = report.knotplot_catalog || {};
  printKv('catalog_ok', kp.catalog_ok);
  printKv('skipped', kp.skipped);
  const kpJs = kp.js_catalog || {};
  printKv('js_load_ok', kpJs.load_ok);
  printKv('js_id_count', kpJs.id_count);
  printKv('js_path', kpJs.path);
  for (const hit of kpJs.sample_hits || []) {
    console.log(
      `  js ${String(hit.id).padEnd(12)} present=${String(hit.present).padEnd(5)} ` +
        `components=${hit.component_count} family=${hit.family} status=${hit.status}`,
    );
  }
  if (kp.errors && kp.errors.length) {
    for (const err of kp.errors) console.log('  -', err);
  }

  printHeader('Binding catalog');
  const bc = report.binding_catalog || {};
  printKv('list_bindings_ok', bc.list_bindings_ok);
  printKv('counts', JSON.stringify(bc.counts));

  printHeader('Examples coverage');
  const ec = report.examples_coverage || {};
  printKv('example_ts_files', ec.example_ts_files);
  printKv('example_py_files', ec.example_py_files);
  printKv('coverage_ok', ec.coverage_ok);

  if (report.binding_tests) {
    printHeader('Binding tests (npm test)');
    const bt = report.binding_tests;
    printKv('ok', bt.ok);
    printKv('exit_code', bt.exit_code);
    printKv('summary_line', bt.summary_line);
  }

  printHeader('Native bindings');
  const native = report.native_bindings;
  printKv('native_found', native.native_found);
  printKv('available', native.available);
  printKv('engine_info', JSON.stringify(native.engine_info));
  if (native.list_bindings_result) {
    printKv('binding_counts', JSON.stringify(native.list_bindings_result.counts));
  }

  printHeader('Topology candidate lookup');
  for (const row of report.topology_candidates) {
    console.log(
      `${String(row.label).padEnd(26)} ${String(row.topology_id).padEnd(10)} ` +
        `ok=${String(row.lookup_call_ok).padEnd(5)} ` +
        `found=${String(row.found_nonempty).padEnd(5)} ` +
        `length_like=${row.length_like} ` +
        `error=${row.error}`,
    );
  }

  printHeader('ParticleEvaluator (canon guard)');
  const pe = report.particle_evaluator || {};
  printKv('particle_evaluator_exists', pe.particle_evaluator_exists);
  printKv('trefoil_canon_ok', pe.trefoil_canon_ok);
  printKv('trefoil_canon_error', pe.trefoil_canon_error);
  printKv('knotplot_reject_ok', pe.knotplot_reject_ok);
  printKv('knotplot_reject_error', pe.knotplot_reject_error);

  printHeader('Trefoil triad (Node-adapted)');
  const triad = report.trefoil_triad || {};
  printKv('catalog_ok', triad.catalog_ok);
  printKv('note', triad.note);
  for (const row of triad.channels || []) {
    console.log(
      `${String(row.channel).padEnd(18)} ref=${String(row.ref).padEnd(10)} ` +
        `PE=${row.particle_evaluator} export=${row.curve_export_ok} ` +
        `err=${row.particle_evaluator_error || row.curve_export_error || ''}`,
    );
  }

  printHeader('Canon-v0.8.x numerical sanity checks');
  const cc = report.constant_checks;
  for (const key of [
    'omega_c_s_inv',
    'Gamma_0_m2_s',
    'alpha_swirl',
    'E_core_MeV',
    'E_meson0_MeV',
    'ambient_energy_density_J_m3',
    'ambient_to_core_energy_density_ratio',
    'condensation_ratio_rho_core_over_rho_f',
    'swirl_clock_using_c',
    'swirl_clock_using_c_inverse_square',
  ]) {
    printKv(key, cc[key]);
  }

  printHeader('Meson link energy scaffolds');
  for (const row of report.meson_link_scaffolds) {
    console.log(
      `${row.candidate} n=${row.n_components} Lk=${row.linking_number} ` +
        `λ=${row.lambda_link} E=${row.energy_MeV}`,
    );
  }

  printHeader('Public API count');
  printKv('public_api_entries', (report.public_api || []).length);
}

function main(argv) {
  const args = parseArgs(argv || process.argv.slice(2));

  if (args.regenManifest && !args.quiet) {
    printHeader('Regenerating binding manifest');
    printKv('skipped', true);
    printKv('reason', 'Python tooling only');
  }

  let npmInfo = null;
  if (args.install) {
    printHeader('Installing package');
    printKv('package', args.package);
    npmInfo = runNpmInstall(args.package);
    printKv('npm return code', npmInfo.returncode);
    if (npmInfo.returncode !== 0) {
      console.log('npm install failed; continuing to import probe anyway.');
    }
  }

  const { sst, info } = loadSstcore();
  if (!sst) {
    const failure = {
      environment: probeEnvironment(),
      npm_install: npmInfo,
      module: { import_info: info },
    };
    if (args.jsonOut) {
      fs.writeFileSync(args.jsonOut, JSON.stringify(jsonable(failure), null, 2), 'utf8');
    }
    if (!args.quiet) {
      printHeader('Import failed');
      console.log(JSON.stringify(info, null, 2));
    }
    return 1;
  }

  const report = makeReport(sst, info, {
    runBindingTests: args.runBindingTests,
    regenManifest: args.regenManifest,
  });
  report.npm_install = npmInfo;

  if (args.jsonOut) {
    fs.writeFileSync(args.jsonOut, JSON.stringify(jsonable(report), null, 2), 'utf8');
    if (!args.quiet) printKv('wrote_json', args.jsonOut);
  }

  if (args.csvOut) {
    const prefix = args.csvOut;
    const dir = fs.existsSync(prefix) && fs.statSync(prefix).isDirectory() ? prefix : path.dirname(prefix) || '.';
    const base = fs.existsSync(prefix) && fs.statSync(prefix).isDirectory()
      ? path.join(prefix, 'sstcore_probe_node')
      : prefix;
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    writeCsv(`${base}_public_api.csv`, report.public_api);
    writeCsv(`${base}_helpers.csv`, report.expected_helpers);
    writeCsv(`${base}_topologies.csv`, report.topology_candidates);
    writeCsv(`${base}_meson_scaffolds.csv`, report.meson_link_scaffolds);
    if (!args.quiet) printKv('wrote_csv_prefix', base);
  }

  if (!args.quiet) printReportSummary(report);

  if (args.strictBindings) {
    const bc = report.binding_catalog || {};
    if (!bc.list_bindings_ok) return 2;
  }

  if (!sst.isAvailable) return 1;
  return 0;
}

if (require.main === module) {
  process.exit(main());
}

module.exports = {
  loadSstcore,
  makeReport,
  printReportSummary,
  computeConstantChecks,
  jsonable,
};
