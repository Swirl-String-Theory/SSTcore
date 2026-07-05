# Release Notes — SSTcore v0.8.18

Feature release: **resolved-tube geometry** steps 1–8 integrated in-tree, P0 canon alignment fixes (audit-backed), plus diagnostic improvements for knot-resource cross-checks.

Compared to **v0.8.13**, v0.8.18 ships Rawdon/Cantarella-style ropelength/thickness analysis, KKT/NNLS contact-balance solvers (dense and sparse), analytic MinRad± kink gradients, and a unified trefoil triad probe across ideal / Fremlin / knotplot resources.

---

## Changelog (v0.8.13 → v0.8.18)

### Resolved-tube geometry (steps 1–8)

- **Core metrics** — `ResolvedTubeGeometry::analyze`, thickness/reach, ropelength radius/diameter conventions, nontrivial-knot lower-bound guard
- **KKT / NNLS (step 5)** — `ContactStressMap::build_rigidity_matrix`, dense `solve_nonnegative_least_squares`, `diagnose_length_criticality`
- **Analytic + sparse (step 6)** — `kink_minrad_plus/minus_gradient_flat`, `build_sparse_rigidity_matrix`, `solve_nonnegative_least_squares_sparse`, `sparse_to_dense`; sparse solver is the default in diagnostics
- **Active-set + export (step 7)** — `solve_nonnegative_least_squares_*_active_set` (default in diagnostics), Matrix Market export (`write_sparse_matrix_market`, `write_vector_market`), `NNLSResult.algorithm` / `active_set_size`
- **Tightening loop (step 8)** — `ResolvedTubeTightener::tighten` projected-gradient loop with line search, thickness correction (scale/newton), `TighteningOptions` / `TighteningResult`; flat helpers `resolved_tube_tighten`, `resolved_tube_projected_gradient`
- **Optional Eigen adapter** — `to_eigen_sparse` behind `SSTCORE_USE_EIGEN` (off in default builds)
- Patch archive: [`docs/patches/resolved_tube/`](patches/resolved_tube/) (0001–0005)
- Examples: `example_resolved_tube_geometry.py`, `example_resolved_tube_kkt_solver.py`, `example_resolved_tube_from_fseries.py`, `example_resolved_tube_sparse_large_knot.py`, `example_resolved_tube_active_set_nnls.py`, `example_resolved_tube_scipy_export.py`, `example_resolved_tube_tightening_loop.py`, `example_resolved_tube_tightener_backends.py`
- Tests: `tests/test_resolved_tube_geometry.{py,cpp}`

### P0 canon alignment (audit v0.8.18)

- `rho_fluid` → `7.0e-7` in `ab_initio_mass.h`
- Chronos–Kelvin invariant uses vorticity convention; `swirl_clock_from_omega` inverse with `4c²`
- Time dilation default `c_vacuum`; `compute_relativistic_metrics` passes `c_light`
- Audit archive: [`docs/audits/v0.8.18/`](audits/v0.8.18/); patch: [`docs/patches/v0.8.18/`](patches/v0.8.18/)

### Knot registry & diagnostics

- **Trefoil triad** in `SSTcore_full_probe.py` — side-by-side resolve across `3:1:1`, `3_1` (Fremlin), `knot_3.1` (knotplot)
- **Curve export smoke** — `evaluate_fourier_block` sampling per channel with `length_exact` checks

### Packaging

- Package version **0.8.18** in `setup.py` and `src/SSTcore/__init__.py`
- Default source ZIP: `dist/SSTcore_source_v0.8.18.zip`
- Regenerated `resources/binding_manifest.json` for new pybind exports

---

## Migration

- `kink_minrad_gradient_flat(points, kink, finite_difference_step=…)` → add optional `use_analytic=True` before `finite_difference_step`
- `build_rigidity_matrix` / `diagnose_length_criticality` accept new kwargs `use_analytic_kink_gradient` and `use_sparse_solver` (defaults: analytic + sparse)
- `diagnose_length_criticality` accepts `use_active_set_solver=True` (default) and reports `nnls_algorithm` / `nnls_active_set_size`
- New flat helpers: `resolved_tube_write_matrix_market`, `resolved_tube_write_vector_market`, `resolved_tube_solve_active_set`, `resolved_tube_tighten`, `resolved_tube_projected_gradient`
- New types: `TighteningOptions`, `TighteningStepRecord`, `TighteningResult`, `ResolvedTubeTightener`

Existing callers that pass only positional args continue to work; diagnostics now use the sparse backend by default.

---

## Test checklist

```powershell
cmake --build build --target test_resolved_tube_geometry
pytest tests/test_resolved_tube_geometry.py tests/test_canon_v0_8_12_alignment.py -q
python examples/example_resolved_tube_active_set_nnls.py
python examples/example_resolved_tube_tightening_loop.py
python examples/example_resolved_tube_tightener_backends.py
set PYTHONPATH=src
python examples/example_resolved_tube_geometry.py
python examples/example_resolved_tube_kkt_solver.py
python examples/example_resolved_tube_sparse_large_knot.py
python SSTcore_full_probe.py
python scripts/gen_binding_manifest.py --check
```

---

## Summary

**SSTcore v0.8.18** is the recommended bundle for resolved-tube ropelength work, sparse contact-balance diagnostics, and reproducible trefoil resource audits aligned with SST Canon v0.8.17+ geometry channels.
