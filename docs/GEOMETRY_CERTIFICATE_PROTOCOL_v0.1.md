# Geometry Certificate Protocol v0.1

Software-layer protocol for RKS geometry certification in SSTcore.
This document **references** SST CANON v0.8.21 equations and labels; it does **not**
re-derive or duplicate them.

Primary canon locations (SwirlStringTheory):

- Research track polygonal-to-smooth ladder: `SST_CANON-v0.8.21-research-track.tex`
  (`eq:rt_equilateral_error`, `eq:rt_contact_residual`, `eq:rt_geometry_precision_ceiling`,
  multistart / contact-map paragraphs).
- Main ropelength convention guard: `SST_CANON-v0.8.21.tex`
  (`subsec:canon_ropelength_certification_guard`, `Rop_rad` / `Rop_diam`).

## Gate naming

Canon already uses `(G_0)`–`(G_3)` for the finite-cell α-obstruction program.
Knot / tube geometry certification therefore uses `(K_*)`, not `(G_*)`.

| Gate | Role | Canon reference |
|------|------|-----------------|
| `K_0` | Provenance and hashes | Input provenance discipline (cf. Ridgerunner / RT certification section) |
| `K_1` | Independent topology audit | Knot identity / Alexander–Briggs consistency checks |
| `K_2` | Polygonal thickness and equilateral gate | `eq:rt_equilateral_error` (`ε_eq = max_i \|ℓ_i/ℓ̄ − 1\|`); polygonal thickness |
| `K_3` | Smooth spline reach and ropelength | Polygonal-to-smooth ladder; report `reach_spline^num` and dual `Rop_*` |
| `K_4` | KKT and contact-measure convergence | `χ_KKT` / `eq:rt_contact_residual`; contact-map convergence |
| `F_1` | Volumetric core profile | Field layer (deferred) |
| `F_2` | Hodge-complete velocity | Field layer (deferred) |
| `F_3` | Pressure and spectral diagnostics | Field layer (deferred) |

## Certification predicates

```
RKS-Geometry Certified  ⇔  K_0 ∧ K_1 ∧ K_2 ∧ K_3 ∧ K_4
RKS-Field Certified     ⇔  RKS-Geometry Certified ∧ F_1 ∧ F_2 ∧ F_3
```

Field gates do not block geometry-certificate runs.

## Status labels (numerical vs certified)

| Symbol | Meaning in SSTcore |
|--------|--------------------|
| `reach_spline^num` | Output of `ContinuousReachSolver` / `analyze_smooth_resolved_tube` |
| `L_spline` | `PeriodicCubicSpline3D::integrated_arclength` (not chord-parameter `length()`) |
| `Rop_rad` | `L_spline / reach_spline^num` |
| `Rop_diam` | `½ Rop_rad` (always export both) |
| `Rop_smooth^ub` | Reserved for a future rigorous upper bound with certified error intervals |

Until adaptive arclength error bounds and search diagnostics are accepted under a
project-specific tolerance policy, report reach as **numerical**, not proven.

## Equilateral gate (`K_2`)

Normative:

```
ε_eq := edge_length_max_rel_dev = max_i |ℓ_i / ℓ̄ − 1|
equilateral_ok ⇔ ε_eq ≤ equilateral_tol
```

`edge_length_rel_std` remains diagnostic only.

## Seed dependence (reported separately)

Do **not** fold into `ε_geom` yet. Report:

```
ε_seed^rop ,  ε_seed^contact ,  ε_seed^reach
```

Decide after five-seed runs whether a single scalar seed error is meaningful.

## Canon guards (always state)

1. Small `R_CK` does **not** imply dynamical stability.
2. Hodge dimension does **not** classify a knot.
3. Not every geometric strut carries positive contact force.

## SSTcore API map (v0.8.19+)

| Protocol need | API |
|---------------|-----|
| `ε_eq` | `ResolvedTubeGeometry.edge_length_max_relative_deviation` / metrics field `edge_length_max_rel_dev` |
| Polygonal tube | `ResolvedTubeGeometry.analyze` (`equilateral_ok` gated on max-rel-dev) |
| `reach_spline^num` + diagnostics | `compute_continuous_reach` |
| `L_spline` + `Rop_*` | `analyze_smooth_resolved_tube` |

## Out of scope for v0.1 software layer

- Broad canon LaTeX patch introducing `(K_*)` into the PDF
- Bishop framing / core profiles (`F_1`)
- Production `3_1` Geometry Certificate v0.1 run (follows `0_1` baseline on this API)
