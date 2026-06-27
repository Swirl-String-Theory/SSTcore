# Knot geometry sources (SSTcore canon policy)

SSTcore distinguishes three representation layers. **Do not mix them** for canon mass, ropelength, or Biot–Savart benchmarks.

| Layer | Bundle | Role | Typical use |
|-------|--------|------|-------------|
| **ideal.txt** (Brian Gilbert AB `n:m:k`) | `resources/ideal.txt` | **CanonIdeal** | Mass, L_K, A_K, electron benchmark |
| **KnotPlot** (`knot_*/*_ideal.txt`) | `resources/knotplot/` | **LegacyImport** | Visualization, parser tests, legacy comparison |
| **Fremlin** (`knot.n_m.fseries`) | `resources/Knots_FourierSeries/` | **AnalyticTest** | Unit tests, fast analytic evaluation |

## Hard rules

1. `knotplot/**/knot_*_ideal.txt` is **never** a CanonIdeal AB fallback for lookup or mass.
2. On duplicate AB ids, **`ideal.txt` wins**.
3. `ParticleEvaluator` accepts only Gilbert AB ids (`^\d+(:\d+)+$`) unless `allow_non_canonical_geometry_for_research_only=True` (research/comparison only; default `False`).
4. Use `resolve_knot_ref()` and `assert_canon_ideal()` before canon calculations.

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

res = resolve_knot_ref("3:1:1")
assert_canon_ideal(res, CalculationRole.CANON_MASS)

ev = SSTcore.ParticleEvaluator("3:1:1", 200)  # canon
# SSTcore.ParticleEvaluator("knot_3.1", 200)  # raises unless research flag
```

Crosswalk stub: `resources/knot_id_crosswalk.csv`.
