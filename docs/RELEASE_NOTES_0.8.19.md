# Release Notes — SSTcore v0.8.19

Geometry-certificate software layer on top of the v0.8.18 continuous-reach solver.
No broad SST CANON LaTeX patch in this release.

## Changelog (v0.8.18 → v0.8.19)

### Equilateral gate (canon `ε_eq`)

- Added `ResolvedTubeGeometry::edge_length_max_relative_deviation`
- `ResolvedTubeMetrics.edge_length_max_rel_dev` populated on analyze
- `equilateral_ok` now gates on **max relative deviation**, not `edge_length_rel_std`
- `edge_length_rel_std` retained as diagnostic only

### Smooth spline arclength

- `PeriodicCubicSpline3D::length()` remains the **chord-parameter domain**
- Added `integrated_arclength()` → `SplineLengthResult` with adaptive Gauss–Kronrod
  length, absolute error estimate, interval count, and convergence flag

### Continuous-reach diagnostics

- `ContinuousReachResult` now exposes search metadata:
  curvature intervals, DCSD seed/refined/rejected counts, search resolution,
  refinement tolerance, `search_converged`
- Python / Node bindings export these fields

### Combined smooth metrics API

- New `SmoothTubeAnalyzer::analyze` / `analyze_smooth_resolved_tube` /
  `analyzeSmoothResolvedTube`
- Always exports `ropelength_rad` and `ropelength_diam` (`Rop_rad = 2 Rop_diam`)
- Reach labeled numerical (`reach_spline^num`); not a rigorous global certificate

### Protocol

- [`docs/GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md`](GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md)
  defines `(K_0)`–`(K_4)` / `(F_*)` gates by **reference** to canon labels
  (no equation duplication)

### Tests

- Unit circle smooth ropelength conventions (Test A)
- Two-circle inter-component (Test B, existing + smooth path)
- Equilateral std vs max-dev mismatch (Test C)
- Ideal `3:1:1` dual `Rop_*` export (Test D)
- Multiresolution circle stability (Test E)

## Deferred

- Folding `ε_seed` into `ε_geom`
- Field gates `F_1`–`F_3` (Bishop / core / Hodge / spectral)
- Canon `(K_*)` LaTeX introduction
- Production `3_1` Geometry Certificate v0.1 run
