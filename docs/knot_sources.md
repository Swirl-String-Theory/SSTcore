# Knot geometry sources (SSTcore canon policy)

SSTcore distinguishes three representation layers. **Do not mix them** for canon mass, ropelength, or Biot–Savart benchmarks.

| Layer | Bundle | Role | Typical use |
|-------|--------|------|-------------|
| **ideal.txt** (Brian Gilbert AB `n:m:k`) | `resources/ideal/ideal.txt` | **CanonIdeal** | Mass, L_K, A_K, electron benchmark |
| **KnotPlot** (Workbench export + `*_ab.xml`) | `resources/knotplot/` | **LegacyImport** / **RelaxedImport** | Visualization, parser tests, relaxed centerlines, AB comparison |
| **Fremlin** (`knot.n_m.fseries`) | `resources/Knots_FourierSeries/` | **AnalyticTest** | Unit tests, fast analytic evaluation |

## Hard rules

1. Knotplot AB-XML (`**/*_ab.xml`) and any legacy `knot_*_ideal.txt` are **never** a CanonIdeal AB fallback for lookup or mass. Only Gilbert `ideal.txt` satisfies `assert_canon_ideal`.
2. On duplicate AB ids, **`ideal.txt` wins**.
3. Relaxed KnotPlot geometry uses `KnotCurveRole.RELAXED_IMPORT`, which is **outside** `_CANON_CALC_ROLES`.
4. `ParticleEvaluator` accepts only Gilbert AB ids (`^\d+(:\d+)+$`) unless `allow_non_canonical_geometry_for_research_only=True` (research/comparison only; default `False`).
5. Use `resolve_knot_ref()` and `assert_canon_ideal()` before canon calculations.

## Trefoil (`3:1:1`) reference metrics

| Source | Reported L/D | Native length | Contact-norm L/D | Mass scale vs ideal |
|--------|--------------|---------------|------------------|---------------------|
| ideal.txt | 16.371637 | ~16.37 | ~16.37 | **1.000** |
| KnotPlot AB | 57 / 1 | ~57 | ~17.8 | **~1.09** (contact); **~3.48×** raw L |
| Fremlin `3_1` | — | ~15.2 | ~17.1 | **~1.04** |
| Fremlin `3_1u` | — | torus | ~22.2 | **~1.35** |

Quantities linear in total length (`M_K`, filament energy, Pauli volume) inherit these factors directly.

## API

```python
from SSTcore import resolve_knot_ref, assert_canon_ideal, CalculationRole
from SSTcore import get_knotplot_ab_path, list_knotplot_ids

res = resolve_knot_ref("3:1:1")
assert_canon_ideal(res, CalculationRole.CANON_MASS)

# Knotplot (non-canon): INDEX-backed AB path
ids = list_knotplot_ids()
ab = get_knotplot_ab_path("knot_3.1")  # or legacy alias

ev = SSTcore.ParticleEvaluator("3:1:1", 200)  # canon
# SSTcore.ParticleEvaluator("knot_3.1", 200)  # raises unless research flag
```

Crosswalk stub: `resources/knot_id_crosswalk.csv`.
