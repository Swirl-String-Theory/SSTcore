# SSTcore resources

## Source ZIP bundle (audit / evidence download)

If you obtained SSTcore from **`SSTcore_source_v0.x.x.zip`** (not from a PyPI wheel), large resource trees are shipped as nested archives under `resources/*.zip`. **Unpack them before building, running tests, or examples.**

From the repository root:

```bash
python scripts/unpack_source_resources.py
pip install -e .
python -m pytest tests/ -q
```

The manifest `resources/source_bundle_manifest.json` (inside the source ZIP) lists each archive, its SHA256 checksum, and the target directory.

### Nested archives (typical)

| Archive | Expands to |
|---------|------------|
| `resources/ideal_12_data.zip` | `resources/ideal/ideal_12_data/` |
| `resources/knotplot.zip` | `resources/knotplot/` |
| `resources/Knots_FourierSeries.zip` | `resources/Knots_FourierSeries/` |
| `resources/Results.zip` | `resources/Results/` (optional; dashboard/export outputs) |

### Ideal layout

Gilbert databases live under **`resources/ideal/`** (`ideal.txt`, `idealLinks*.txt`, `ideal_12_data/`, …). Resolvers still accept the older flat `resources/ideal.txt` path as a legacy fallback.

### Knotplot layout (`resources/knotplot/`)

Workbench-exported entities, indexed by **`INDEX.json`**:

| Status | Typical contents |
|--------|------------------|
| **Relaxed** | N300 polish centerline, audit polish/vect/metrics, `catalog_status`, `seed_selection`, analytic D1, `build_*.kpc`, regenerated `*_ab.xml` |
| **Stub** | `build_*.kpc` (and analytic D1 when present) — not yet relaxed |

Public API: `list_knotplot_ids`, `get_knotplot_entry`, `get_knotplot_ab_path` / `get_knotplot_ab`, `get_knotplot_polish_path`, `get_knotplot_build_script`. Legacy `get_knotplot_ideal_path` / `knotplot` resolve AB-XML with a deprecation warning.

Use **`resources/knotplot/`** only. Do not copy knotplot data into `Results/knotplot/`. Repo-only ridgerunner helpers live under `tools/knotplot/` (not in wheel/npm).

### Deliberately excluded from source ZIP

- All **`*.stl`** files (3D-print meshes; not used by tests or examples)
- Build artifacts (`.pyc`, `.pyd`, `.so`, `build/`, etc.)

### PyPI wheel users

Wheels embed unpacked resources; you do **not** need this step after `pip install SSTcore`.

### Quick verification after unpack

- `resources/ideal/ideal.txt` exists (or legacy `resources/ideal.txt`)
- At least one `.fseries` file under `resources/Knots_FourierSeries/`
