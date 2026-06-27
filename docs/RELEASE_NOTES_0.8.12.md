# Release Notes — SSTcore v0.8.12

This release builds on the v0.8.0 research snapshot with **canon alignment**, a unified **ideal-resource and geometry layer**, and tighter Python packaging. The focus is correct knot geometry for mass evaluation, full Gilbert dataset coverage (AB/HT/TL), and reproducible resource access—not a full dashboard rewrite.

Compared to **v0.8.0**, v0.8.12 is the first release where `ParticleEvaluator("3:1:1")` reliably uses Brian Gilbert `ideal.txt`, non-canon KnotPlot/Fremlin geometry is blocked by default for mass paths, and HT/TL/11-/12-crossing data is reachable through one Python lookup API.

---

## ✨ Highlights

### What's new since v0.8.0

- **Canon constants & delay lock** — `ALPHA`, delay phase-lock residual/sign (`Omega = omega0 - kappa·sin(Omega·tau)`), plus `pauli_barrier_scale`, `swirl_impedance`, and `dimensionless_stiffness_ratio` in C++ and Python
- **Ideal.txt AB lookup** — `find_ideal_ab_block_by_id()`; `ParticleEvaluator` no longer depends on missing `ideal_database.txt`
- **Canon geometry guards** — `knot_registry.py`, `resolve_knot_ref()`, trefoil three-source regression tests, `docs/knot_sources.md`
- **Gilbert HT/TL/STRING support** — extended parser, `find_ideal_by_id()` with provenance; 12-crossing data as point clouds
- **Export CLI & embedded-first examples** — `python -m sstcore export-resources`, `sstcore-export-resources`, resource helpers, example scripts migrated off hardcoded paths
- **Packaging & CI** — Python **3.14** wheels, improved wheel smoke tests, editable-install `_native` resolution, `sstcore.py` shim mirroring full `SSTcore` API
- **Diagnostic probe** — `SSTcore_full_probe.py` extended with ParticleEvaluator and registry smoke checks

### Unchanged from v0.8.0 (still in the tree)

The v0.8.0 snapshot items remain: expanded C++ core (Biot–Savart, fluid dynamics, helicity, knot dynamics, trefoil closure, etc.), SST Dashboard tabs, robustness archives, large bundled resources (ideal knots/links, Fremlin fseries, knotplot, ideal_12_data), CMake/pybind11/conda/npm build docs.

---

## Changelog (v0.8.0 → v0.8.12)

### Canon alignment & core API

- Updated **`SST_Constants.h`**: canon `ALPHA` and related comments aligned with SST canon v0.8.12
- Fixed **delay phase-lock** residual/sign for v0.8.10+ delayed-phase formulations
- Added Python-bound quantities: **`pauli_barrier_scale`**, **`swirl_impedance`**, **`dimensionless_stiffness_ratio`**
- Benchmark and dashboard scripts route fine-structure constant through **`SSTCanonicalConstants.alpha()`** instead of hardcoded values
- New spectroscopic-gap, delay-mode selection, and tension-scale classes; additional fluid-dynamics methods
- Package version bumped to **0.8.12** in `setup.py` and `src/SSTcore/__init__.py`

### Ideal geometry & mass pipeline

- **`find_ideal_ab_block_by_id(ab_id)`** — embedded-first search across `ideal*.txt`; never searches `knotplot/**` or `*_ideal.txt` fallbacks
- **`ParticleEvaluator`** constructor uses Gilbert AB blocks from `ideal.txt`; clear errors when geometry is missing
- **`get_ideal_ab()`** multi-file search order (`ideal.txt` first, then other Gilbert bundles)
- Python API maps empty native strings to **`None`** for cleaner ergonomics
- **`knot_registry.py`**: `KnotSource`, `KnotCurveRole`, `CalculationRole`, `KnotResolution`, **`resolve_knot_ref()`**, **`assert_canon_ideal()`**
- **`ParticleEvaluator`** accepts only Gilbert AB ids (`3:1:1`, `6:1:1`, …); rejects KnotPlot-style refs unless **`allow_non_canonical_geometry_for_research_only=True`**
- Three-layer canon policy documented in **`docs/knot_sources.md`**; stub crosswalk **`resources/knot_id_crosswalk.csv`**
- Trefoil regression tests pin mass-scale factors: ideal = 1.0, KnotPlot contact-norm ~+9%, Fremlin default ~+4.3%
- C++ **`parse_ideal_gilbert_from_string()`** — parses `<AB>`, `<HT>`, `<TL>`; `<STRING>` treated as component alias (including unclosed STRING in `ideal_11n`)
- **`find_ideal_block_by_id(id, tag)`** — general Gilbert XML lookup; **`find_ideal_ab_block_by_id`** remains AB-only for mass
- **`find_ideal_by_id(id, tag=None)`** → **`IdealLookupResult`** (block, source file, xml tag, author, geometry kind)
- **`IdealGeometryKind`**: `FOURIER_XML` vs **`POINT_CLOUD`** for `ideal_12_data`
- **`get_ideal_12_points()`** and 12-crossing knot options tagged as point-cloud geometry (not mis-parsed as AB Fourier)
- Duplicate AB entries: **`ideal.txt` wins** over other bundles

| Layer | Source | Role | v0.8.12 behaviour |
|-------|--------|------|-------------------|
| **ideal.txt** | Brian Gilbert AB `n:m:k` | CanonIdeal | Default for `ParticleEvaluator`, `L_K`, mass |
| **KnotPlot** | `knot_*/*_ideal.txt` | LegacyImport | Viz / comparison only |
| **Fremlin** | `Knots_FourierSeries` | AnalyticTest | Unit tests / fast eval; not canon mass |

### Tooling, examples & resources

- **`python -m sstcore export-resources --dest ./out [--manifest manifest.json]`**
- Console entry point: **`sstcore-export-resources`**
- New helpers: **`list_ideal_source_files()`**, **`load_fseries_knot()`**, **`list_embedded_fseries_ids()`**, **`load_ideal_ab_embedded()`**, **`parse_fseries_knot()`**, **`use_disk_resources()`**
- **`examples/sstcore_resource_helpers.py`** — thin re-export for example scripts
- Tier-A examples migrated to embedded-first (`example_knot_visualization`, `example_ideal_knot_showcase`, `showcase_ideal_txt_figure8`, `example_biot_savart`, `fourier_knot.example`, `example_fremlin_4_1_showcase`, `knots.py`, `knots-toggle-autoknot`, `HelicityCalculation`, `helicity2`)
- Legacy PyInstaller paths: **`compile.bat`** and **`SSTcore_Dashboard.spec`** bundle **`resources/ideal.txt`** instead of `ideal_database.txt`
- Export set includes ideal/link bundles, `Knots_FourierSeries/`, `knotplot/`, `ideal_12_data/`, optional SHA256 manifest

### Dashboard & research workflow

- Master / mass sweeps use **`SSTCanonicalConstants.alpha()`**
- Embedded ideal AB tabs target **`ideal.txt`**; reduced reliance on legacy `ideal_database.txt`
- Ideal-vs-Fremlin comparison supported via registry and three-source trefoil validation

Robustness archives, v10.3 workflow, and sweep export layout from v0.8.0 are unchanged.

### Build, packaging & quality

- **Python 3.14** wheel support; PyPI classifiers updated
- CI wheel smoke tests import native module; **`SST_WHEEL_TEST=1`** strips checkout paths from `sys.path`
- Editable installs resolve **`SSTcore._native`** via relative import
- Import path refactor: **`swirl_string_core` → `SSTcore`**; root **`sstcore.py`** shim re-exports full API
- **`import SSTcore`** canonical; **`import sstcore`** optional via root shim; **`python -m SSTcore`**
- New test coverage: ideal resources, knot registry, trefoil three sources, Gilbert formats, export CLI
- **`SSTcore_full_probe.py`**: import, resources, topology lookup, ParticleEvaluator canon guard, `resolve_knot_ref`

npm/WASM packaging docs from v0.8.0 remain; no breaking npm API changes in this release.

---

## ⚠️ Breaking / migration notes

1. **`ParticleEvaluator`** — expects Gilbert AB ids (`3:1:1`, `6:1:1`, …). KnotPlot/Fremlin-style refs fail unless `allow_non_canonical_geometry_for_research_only=True`.
2. **`ideal_database.txt`** — deprecated for canon mass; use `ideal.txt` / `find_ideal_ab_block_by_id()`.
3. **Examples** — embedded-first by default; set **`SST_USE_DISK_RESOURCES=1`** for explicit disk fallback.
4. **Import / layout** — canonical package **`src/SSTcore/`** with **`import SSTcore`**. Optional **`import sstcore`** via root shim. Avoid hand-made ZIPs; use git clone or PyPI sdist.

---

## Quick reference — new Python API

```python
import SSTcore as sst

# Canon AB (mass)
sst.ParticleEvaluator("3:1:1", 200)
sst.find_ideal_ab_block_by_id("3:1:1")
sst.load_ideal_ab_embedded("3:1:1")

# Full Gilbert lookup (audit / 11-crossing / links)
hit = sst.find_ideal_by_id("K11a1", tag="HT")
pts = sst.get_ideal_12_points("12a4")

# Registry & guards
res = sst.resolve_knot_ref("3:1:1")
sst.assert_canon_ideal(res, sst.CalculationRole.CANON_MASS)

# Export bundled resources
# python -m sstcore export-resources --dest ./exported --manifest manifest.json
```

---

## 🎉 Summary

**SSTcore v0.8.12** keeps the v0.8.0 platform (broad C++ core, dashboard, resources, build tooling) and adds what was missing for **canon-correct mass and ideal geometry**: reliable `ideal.txt` loading, explicit source roles, HT/TL/STRING parsing, exportable resources, and guarded mass evaluation paths. It is the recommended base for SST canon v0.8.12 numerical work, ab initio mass evaluation, and reproducible knot-source audits.
