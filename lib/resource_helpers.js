'use strict';

/**
 * Python-parity resource / knot helpers for the Node package surface.
 * Attached from index.js as camelCase + snake_case aliases.
 */

const fs = require('fs');
const path = require('path');

const IDEAL_SUBDIR = 'ideal';

const IDEAL_SOURCE_FILES = {
  ideal: 'ideal.txt',
  ideal_11a: 'ideal_11a.txt',
  ideal_11n: 'ideal_11n.txt',
  idealLinks: 'idealLinks.txt',
  idealLinks_10a: 'idealLinks_10a.txt',
  idealLinks_10n: 'idealLinks_10n.txt',
  ideal_short: 'ideal_short.txt',
};

const IDEAL_AB_SEARCH_SOURCES = [
  'ideal',
  'ideal_short',
  'ideal_11a',
  'ideal_11n',
  'idealLinks',
  'idealLinks_10a',
  'idealLinks_10n',
];

const LINK_SEARCH_SOURCES = ['idealLinks', 'idealLinks_10a', 'idealLinks_10n'];

const AB_ID_RE = /^\d+(:\d+)+$/;
const FREMLIN_RE = /^\d+_\d+[a-z]?$/i;
const KNOTPLOT_RE = /^knot_/i;
const TRIPLE_GEAR_ALIASES = new Set([
  'triple-gear',
  'triple_gear',
  'tl3.3',
  'tl3.3_gear',
  'tl3_3_gear',
]);

/**
 * @param {string} packageRoot absolute path to package root (dirname of index.js)
 * @param {object} [native] native/wasm exports object (optional)
 */
function createResourceHelpers(packageRoot, native) {
  const nat = native && typeof native === 'object' ? native : {};

  function getResourcesDir() {
    const env = process.env.SSTCORE_RESOURCES;
    if (env) {
      try {
        if (fs.existsSync(env) && fs.statSync(env).isDirectory()) {
          return path.resolve(env);
        }
      } catch (_) {
        /* ignore */
      }
    }
    const pkg = path.join(packageRoot, 'resources');
    try {
      if (fs.existsSync(pkg) && fs.statSync(pkg).isDirectory()) {
        return path.resolve(pkg);
      }
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function getIdealFilePath(source) {
    const root = getResourcesDir();
    if (!root) return null;
    const name = IDEAL_SOURCE_FILES[source] || source;
    if (String(name).includes('/') || String(name).includes('\\')) return null;
    // Prefer resources/ideal/<name>, then flat legacy resources/<name>.
    for (const candidate of [path.join(root, IDEAL_SUBDIR, name), path.join(root, name)]) {
      try {
        if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
          return path.resolve(candidate);
        }
      } catch (_) {
        /* ignore */
      }
    }
    return null;
  }

  function getIdealTxtPath() {
    const p = getIdealFilePath('ideal');
    if (p) return p;
    const root = getResourcesDir();
    if (!root) return null;
    const alt = path.join(root, 'Knots_FourierSeries', 'ideal.txt');
    try {
      if (fs.existsSync(alt) && fs.statSync(alt).isFile()) return path.resolve(alt);
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function getKnotsFourierSeriesDir() {
    const root = getResourcesDir();
    if (!root) return null;
    const kfs = path.join(root, 'Knots_FourierSeries');
    try {
      if (fs.existsSync(kfs) && fs.statSync(kfs).isDirectory()) return path.resolve(kfs);
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function getKnotplotDir() {
    const root = getResourcesDir();
    if (!root) return null;
    const d = path.join(root, 'knotplot');
    try {
      if (fs.existsSync(d) && fs.statSync(d).isDirectory()) return path.resolve(d);
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function listIdealSourceFiles() {
    return Object.assign({}, IDEAL_SOURCE_FILES);
  }

  function extractXmlBlock(text, tag, idValue) {
    if (!text || !tag || idValue == null) return null;
    const id = String(idValue).trim();
    const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    let pattern = new RegExp('<' + tag + '\\s+Id="' + escapeRe(id) + '"\\s[^>]*>', 'i');
    let match = text.match(pattern);
    if (!match) {
      const alt = id.replace(/_/g, ':');
      pattern = new RegExp('<' + tag + '\\s+Id="[^"]*' + escapeRe(alt) + '[^"]*"\\s[^>]*>', 'i');
      match = text.match(pattern);
    }
    if (!match || match.index == null) return null;
    const start = match.index;
    const endTag = '</' + tag + '>';
    const end = text.indexOf(endTag, start);
    if (end === -1) return null;
    return text.slice(start, end + endTag.length);
  }

  function readTextFile(filePath) {
    try {
      return fs.readFileSync(filePath, 'utf8');
    } catch (_) {
      return null;
    }
  }

  function getEmbeddedIdealMap() {
    if (typeof nat.getEmbeddedIdealFiles !== 'function') return null;
    try {
      const files = nat.getEmbeddedIdealFiles();
      if (files && typeof files === 'object' && !Array.isArray(files)) return files;
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function getEmbeddedKnotMap() {
    if (typeof nat.getEmbeddedKnotFiles !== 'function') return null;
    try {
      const files = nat.getEmbeddedKnotFiles();
      if (files && typeof files === 'object' && !Array.isArray(files)) return files;
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  function findInEmbeddedIdeal(tag, idValue, preferredFilenames) {
    const embedded = getEmbeddedIdealMap();
    if (!embedded) return null;
    const names = preferredFilenames || Object.values(IDEAL_SOURCE_FILES);
    for (const fname of names) {
      for (const [key, content] of Object.entries(embedded)) {
        const norm = String(key).replace(/\\/g, '/').toLowerCase();
        if (norm.includes('knotplot')) continue;
        const base = String(key).replace(/\\/g, '/').split('/').pop();
        if (base.includes('_ideal.txt')) continue;
        if (base !== fname) continue;
        const block = extractXmlBlock(String(content), tag, idValue);
        if (block) return block;
      }
    }
    return null;
  }

  function getIdealAb(abId, source) {
    const id = String(abId || '').trim();
    if (!id) return null;

    if (source == null) {
      // Prefer XML extract (safe) over native parse which can abort on some IDs.
      const fromEmb = findInEmbeddedIdeal(
        'AB',
        id,
        IDEAL_AB_SEARCH_SOURCES.map((s) => IDEAL_SOURCE_FILES[s]).filter(Boolean),
      );
      if (fromEmb) return fromEmb;
      for (const src of IDEAL_AB_SEARCH_SOURCES) {
        const p = getIdealFilePath(src);
        if (!p) continue;
        const text = readTextFile(p);
        if (!text) continue;
        const block = extractXmlBlock(text, 'AB', id);
        if (block) return block;
      }
      return null;
    }

    const p = source === 'ideal' ? getIdealTxtPath() : getIdealFilePath(source);
    if (!p) return null;
    const text = readTextFile(p);
    if (!text) return null;
    return extractXmlBlock(text, 'AB', id);
  }

  function getIdealLink(linkId, source) {
    const id = String(linkId || '').trim();
    if (!id) return null;

    if (source != null) {
      const p = getIdealFilePath(source);
      if (!p) return null;
      const text = readTextFile(p);
      if (!text) return null;
      return extractXmlBlock(text, 'TL', id);
    }

    const fromEmb = findInEmbeddedIdeal(
      'TL',
      id,
      LINK_SEARCH_SOURCES.map((s) => IDEAL_SOURCE_FILES[s]).filter(Boolean),
    );
    if (fromEmb) return fromEmb;

    for (const src of LINK_SEARCH_SOURCES) {
      const p = getIdealFilePath(src);
      if (!p) continue;
      const text = readTextFile(p);
      if (!text) continue;
      const out = extractXmlBlock(text, 'TL', id);
      if (out) return out;
    }
    return null;
  }

  function walkFseriesLabels(kfsDir) {
    const out = new Set();
    function walk(dir) {
      let entries;
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch (_) {
        return;
      }
      for (const ent of entries) {
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) {
          walk(full);
          continue;
        }
        const lower = ent.name.toLowerCase();
        if (lower.startsWith('knot.') && lower.endsWith('.fseries')) {
          out.add(ent.name.slice(5, -'.fseries'.length));
        }
      }
    }
    walk(kfsDir);
    return Array.from(out).sort();
  }

  function listEmbeddedFseriesIds() {
    const emb = getEmbeddedKnotMap();
    if (emb) {
      return Object.keys(emb).sort();
    }
    const kfs = getKnotsFourierSeriesDir();
    if (!kfs) return [];
    return walkFseriesLabels(kfs);
  }

  function findFseriesTextOnDisk(label) {
    const kfs = getKnotsFourierSeriesDir();
    if (!kfs) return null;
    const exact = `knot.${label}.fseries`.toLowerCase();
    let found = null;
    function walk(dir) {
      if (found) return;
      let entries;
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch (_) {
        return;
      }
      for (const ent of entries) {
        if (found) return;
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) {
          walk(full);
          continue;
        }
        if (ent.name.toLowerCase() === exact) {
          found = readTextFile(full);
        }
      }
    }
    walk(kfs);
    return found;
  }

  function loadFseriesKnot(label) {
    const normalized = String(label || '')
      .trim()
      .replace(/\./g, '_');
    if (!normalized) return null;
    const emb = getEmbeddedKnotMap();
    if (emb && emb[normalized] != null) {
      return String(emb[normalized]);
    }
    // Try prefix match in embedded keys
    if (emb) {
      for (const [key, content] of Object.entries(emb)) {
        if (String(key).toLowerCase() === normalized.toLowerCase()) {
          return String(content);
        }
      }
    }
    return findFseriesTextOnDisk(normalized);
  }

  let _knotplotIndexCache = null;
  const _knotplotDeprecationWarned = new Set();

  function loadKnotplotIndex() {
    if (_knotplotIndexCache) return _knotplotIndexCache;
    const root = getKnotplotDir();
    const empty = { entries: [], legacy_aliases: {}, counts: {} };
    if (!root) {
      _knotplotIndexCache = empty;
      return empty;
    }
    const indexPath = path.join(root, 'INDEX.json');
    try {
      if (fs.existsSync(indexPath)) {
        _knotplotIndexCache = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
        return _knotplotIndexCache;
      }
    } catch (_) {
      /* ignore */
    }
    _knotplotIndexCache = empty;
    return empty;
  }

  function normalizeKnotplotId(knotId) {
    const base = String(knotId || '')
      .trim()
      .replace(/^["']|["']$/g, '');
    if (!base || base.includes('/') || base.includes('\\')) return null;
    const index = loadKnotplotIndex();
    const aliases = index.legacy_aliases || {};
    const ids = new Set((index.entries || []).map((e) => e.id).filter(Boolean));
    const candidates = [base];
    if (aliases[base]) candidates.push(aliases[base]);
    if (!/^(knot_|link_|torus_)/.test(base)) {
      candidates.push(`knot_${base}`);
      if ((base.match(/\./g) || []).length >= 2) candidates.push(`link_${base}`);
    }
    for (const c of candidates) {
      if (ids.has(c)) return c;
      if (aliases[c] && ids.has(aliases[c])) return aliases[c];
    }
    const root = getKnotplotDir();
    if (!root) return null;
    for (const c of candidates) {
      try {
        if (fs.existsSync(path.join(root, c)) && fs.statSync(path.join(root, c)).isDirectory()) {
          return c;
        }
      } catch (_) {
        /* ignore */
      }
    }
    return null;
  }

  function listKnotplotIds(status) {
    return (loadKnotplotIndex().entries || [])
      .filter((e) => e.id && (status == null || e.status === status))
      .map((e) => e.id);
  }

  function getKnotplotEntry(knotId) {
    const canon = normalizeKnotplotId(knotId);
    if (!canon) return null;
    const entry = (loadKnotplotIndex().entries || []).find((e) => e.id === canon);
    return entry ? Object.assign({}, entry) : null;
  }

  function knotplotFileByRole(knotId, role) {
    const entry = getKnotplotEntry(knotId);
    const root = getKnotplotDir();
    if (!entry || !root) return null;
    for (const f of entry.files || []) {
      if (f.role !== role) continue;
      const p = path.join(root, f.relpath);
      try {
        if (fs.existsSync(p) && fs.statSync(p).isFile()) return path.resolve(p);
      } catch (_) {
        /* ignore */
      }
    }
    return null;
  }

  function getKnotplotPolishPath(knotId, uniform) {
    const useUniform = uniform !== false;
    return knotplotFileByRole(knotId, useUniform ? 'uniform_n300' : 'audit_polish');
  }

  function getKnotplotAbPath(knotId) {
    const p = knotplotFileByRole(knotId, 'ab_xml');
    if (p) return p;
    const canon = normalizeKnotplotId(knotId);
    if (!canon) return null;
    const root = getKnotplotDir();
    if (!root) return null;
    for (const name of [`${canon}_ab.xml`, `${canon}_ideal.txt`]) {
      const candidate = path.join(root, canon, name);
      try {
        if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
          return path.resolve(candidate);
        }
      } catch (_) {
        /* ignore */
      }
    }
    return null;
  }

  function getKnotplotAb(knotId) {
    const p = getKnotplotAbPath(knotId);
    return p ? readTextFile(p) : null;
  }

  function getKnotplotBuildScript(knotId) {
    return knotplotFileByRole(knotId, 'build_script');
  }

  function getKnotplotIdealPath(knotId) {
    if (!_knotplotDeprecationWarned.has('getKnotplotIdealPath')) {
      _knotplotDeprecationWarned.add('getKnotplotIdealPath');
      if (typeof console !== 'undefined' && console.warn) {
        console.warn(
          'getKnotplotIdealPath is deprecated; use getKnotplotAbPath (deelplan res-4).',
        );
      }
    }
    return getKnotplotAbPath(knotId);
  }

  function knotplot(knotId) {
    if (!_knotplotDeprecationWarned.has('knotplot')) {
      _knotplotDeprecationWarned.add('knotplot');
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('knotplot() is deprecated; use getKnotplotAb (deelplan res-4).');
      }
    }
    return getKnotplotAb(knotId);
  }

  function parseAbHeaderLd(idealXml) {
    const m = /L="([^"]+)"/.exec(idealXml);
    const n = /D="([^"]+)"/.exec(idealXml);
    if (!m) return { nativeLength: null, ropelength: null };
    const lVal = Number(m[1].trim());
    if (!Number.isFinite(lVal)) return { nativeLength: null, ropelength: null };
    let dVal = 1.0;
    if (n) {
      const d = Number(n[1].trim());
      if (Number.isFinite(d)) dVal = d;
    }
    if (dVal === 0) return { nativeLength: lVal, ropelength: null };
    return { nativeLength: lVal, ropelength: lVal / dVal };
  }

  function fremlinToAbGuess(label) {
    const base = String(label)
      .replace(/^knot\./i, '')
      .split('p')[0]
      .split('u')[0];
    if (!base.includes('_')) return null;
    const parts = base.split('_');
    if (parts.length < 2 || !/^\d+$/.test(parts[0])) return null;
    return parts.slice(0, 2).join(':') + ':1';
  }

  function normalizeRef(ref) {
    return String(ref || '')
      .trim()
      .replace(/^["']|["']$/g, '');
  }

  function resolveTripleGear(ref) {
    const key = ref.toLowerCase().replace(/ /g, '-');
    if (TRIPLE_GEAR_ALIASES.has(key) || key === 'knot_tl3.3_gear') {
      return 'knot_TL3.3_Gear';
    }
    return ref;
  }

  function resolveKnotRef(ref, source, prefer, options) {
    const opts = options && typeof options === 'object' ? options : {};
    let requireRole = opts.requireRole || opts.require_role || null;
    ref = normalizeRef(resolveTripleGear(normalizeRef(ref)));
    if (!ref) return null;

    if (source != null) source = String(source).toLowerCase();
    if (requireRole != null) requireRole = String(requireRole).toLowerCase();

    function idealHit(abId, bundle) {
      const xml = getIdealAb(abId);
      if (!xml) return null;
      const { nativeLength, ropelength } = parseAbHeaderLd(xml);
      return {
        ref,
        source: 'ideal',
        role: 'canon_ideal',
        canonicalAbId: abId,
        nativeLength,
        ropelength,
        closureGap: null,
        fremlinLabel: null,
        knotplotName: null,
        idealXml: xml,
        bundlePath: bundle || 'ideal.txt',
      };
    }

    function fremlinHit(label) {
      const text = loadFseriesKnot(label);
      if (!text) return null;
      return {
        ref,
        source: 'fremlin',
        role: 'analytic_test',
        canonicalAbId: fremlinToAbGuess(label),
        nativeLength: null,
        ropelength: null,
        closureGap: null,
        fremlinLabel: label,
        knotplotName: null,
        idealXml: null,
        bundlePath: `Knots_FourierSeries/${label}/knot.${label}.fseries`,
      };
    }

    function knotplotHit(name) {
      const filePath = getKnotplotIdealPath(name);
      if (!filePath) return null;
      const xml = readTextFile(filePath);
      if (!xml) return null;
      const abM = /Id="(\d+(:\d+)+)"/.exec(xml);
      const abId = abM ? abM[1] : null;
      const { nativeLength, ropelength } = parseAbHeaderLd(xml);
      return {
        ref,
        source: 'knotplot',
        role: 'legacy_import',
        canonicalAbId: abId,
        nativeLength,
        ropelength,
        closureGap: null,
        fremlinLabel: null,
        knotplotName: name.startsWith('knot_') ? name : `knot_${name}`,
        idealXml: xml,
        bundlePath: filePath,
      };
    }

    if (source === 'ideal' && AB_ID_RE.test(ref)) {
      const hit = idealHit(ref);
      if (hit && requireRole && hit.role !== requireRole) return null;
      return hit;
    }
    if (source === 'fremlin') {
      let label = ref.startsWith('knot.') ? ref.replace(/\./g, '_') : ref;
      if (label.startsWith('knot_')) label = label.slice(5).replace(/\./g, '_');
      const hit = fremlinHit(label);
      if (hit && requireRole && hit.role !== requireRole) return null;
      return hit;
    }
    if (source === 'knotplot') {
      const name = ref.startsWith('knot_') ? ref : `knot_${ref.replace(/_/g, '.')}`;
      const hit = knotplotHit(name);
      if (hit && requireRole && hit.role !== requireRole) return null;
      return hit;
    }

    const order = (prefer && prefer.length ? prefer : ['ideal', 'fremlin', 'knotplot']).map((s) =>
      String(s).toLowerCase(),
    );

    const candidates = [];
    if (AB_ID_RE.test(ref)) {
      const hit = idealHit(ref);
      if (hit) candidates.push(hit);
    } else if (KNOTPLOT_RE.test(ref) || TRIPLE_GEAR_ALIASES.has(ref.toLowerCase().replace(/ /g, '-'))) {
      let name = ref.startsWith('knot_') ? ref : resolveTripleGear(ref);
      if (!name.startsWith('knot_')) name = `knot_${name}`;
      const hit = knotplotHit(name);
      if (hit) candidates.push(hit);
    } else if (FREMLIN_RE.test(ref.replace(/\./g, '_'))) {
      const label = ref.replace(/^knot\./i, '').replace(/\./g, '_');
      const hit = fremlinHit(label);
      if (hit) candidates.push(hit);
    } else if (ref.includes('_') && !ref.includes(':')) {
      const parts = ref.split('_');
      if (parts.length >= 2 && parts.slice(0, 2).every((p) => /^\d+$/.test(p))) {
        const abGuess = parts.join(':') + (parts.length === 2 ? ':1' : '');
        const hit = idealHit(abGuess);
        if (hit) candidates.push(hit);
      }
    }

    for (const src of order) {
      for (const c of candidates) {
        if (c.source === src) {
          if (requireRole && c.role !== requireRole) continue;
          return c;
        }
      }
    }

    if (AB_ID_RE.test(ref)) {
      const hit = idealHit(ref);
      if (hit && (!requireRole || hit.role === requireRole)) return hit;
    }
    return null;
  }

  const camel = {
    getResourcesDir,
    getIdealTxtPath,
    getKnotsFourierSeriesDir,
    getKnotplotDir,
    listIdealSourceFiles,
    getIdealAb,
    getIdealLink,
    listEmbeddedFseriesIds,
    loadFseriesKnot,
    knotplot,
    resolveKnotRef,
    // extras used internally / useful for callers
    getIdealFilePath,
    getKnotplotIdealPath,
    normalizeKnotplotId,
    listKnotplotIds,
    getKnotplotEntry,
    getKnotplotPolishPath,
    getKnotplotAbPath,
    getKnotplotAb,
    getKnotplotBuildScript,
  };

  const snake = {
    get_resources_dir: getResourcesDir,
    get_ideal_txt_path: getIdealTxtPath,
    get_knots_fourier_series_dir: getKnotsFourierSeriesDir,
    get_knotplot_dir: getKnotplotDir,
    list_ideal_source_files: listIdealSourceFiles,
    get_ideal_ab: getIdealAb,
    get_ideal_link: getIdealLink,
    list_embedded_fseries_ids: listEmbeddedFseriesIds,
    load_fseries_knot: loadFseriesKnot,
    knotplot,
    resolve_knot_ref: resolveKnotRef,
    get_knotplot_ideal_path: getKnotplotIdealPath,
    normalize_knotplot_id: normalizeKnotplotId,
    list_knotplot_ids: listKnotplotIds,
    get_knotplot_entry: getKnotplotEntry,
    get_knotplot_polish_path: getKnotplotPolishPath,
    get_knotplot_ab_path: getKnotplotAbPath,
    get_knotplot_ab: getKnotplotAb,
    get_knotplot_build_script: getKnotplotBuildScript,
  };

  return { camel, snake, IDEAL_SOURCE_FILES };
}

/**
 * Attach helpers onto the package exports object.
 * @param {object} exportsObj
 * @param {string} packageRoot
 */
function attachResourceHelpers(exportsObj, packageRoot) {
  const { camel, snake } = createResourceHelpers(packageRoot, exportsObj);
  Object.assign(exportsObj, camel, snake);
  return exportsObj;
}

module.exports = {
  createResourceHelpers,
  attachResourceHelpers,
  IDEAL_SOURCE_FILES,
};
