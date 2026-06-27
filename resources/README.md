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
| `resources/ideal_12_data.zip` | `resources/ideal_12_data/` |
| `resources/knotplot.zip` | `resources/knotplot/` |
| `resources/Knots_FourierSeries.zip` | `resources/Knots_FourierSeries/` |
| `resources/Results.zip` | `resources/Results/` (optional; dashboard/export outputs) |

### Knotplot canonical path

Use **`resources/knotplot/`** only. Do not copy knotplot data into `Results/knotplot/` — that subtree was a duplicate and is excluded from bundles.

### Deliberately excluded from source ZIP

- All **`*.stl`** files (3D-print meshes; not used by tests or examples)
- Build artifacts (`.pyc`, `.pyd`, `.so`, `build/`, etc.)

### PyPI wheel users

Wheels embed unpacked resources; you do **not** need this step after `pip install SSTcore`.

### Quick verification after unpack

- `resources/ideal.txt` exists
- At least one `.fseries` file under `resources/Knots_FourierSeries/`
