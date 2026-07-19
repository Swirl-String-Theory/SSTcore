# VortexLab kernel migration status (SSTcore)

Branch: `sstcore/vortexlab-kernel-migration`  
Reference monolith: `SST-Workbench/GUI/vortexring-lab/vortexring-lab-v7.6.25b.html`  
Modular M1: `SST-Workbench/GUI/vortexlab-modular-v7.6.25b-m1` (byte-parity extract)

| Milestone | Scope | Status |
|-----------|--------|--------|
| Fase A | Implementation plan + this status + stale doc fixes + binding_manifest | done |
| K0 | Typed datacontracts (`src/vortexlab/types.h`) | done |
| K1 | CurveSampling, KnotCatalog, PolygonalGauss, polygonal clearance | done |
| K2 | PeriodicCubicSpline3D + ContinuousReachSolver | done |
| K3 | FilamentVelocitySolver (LIA / self / mutual / a_sim) | done |
| K4 | FilamentIntegrator + TopologyGuard | done |
| K5 | IntrinsicFrame + RigidMotion | done |

## Public APIs (Python snake_case / Node camelCase)

| Python | Node |
|--------|------|
| `resample_closed_curve` | `resampleClosedCurve` |
| `sample_curve` | `sampleCurve` |
| `compute_polygonal_gauss` | `computePolygonalGauss` |
| `analyze_resolved_tube_clearance` | `analyzeResolvedTube` |
| `compute_topology_clearance` | `computeTopologyClearance` |
| `compute_continuous_reach` | `computeContinuousReach` |
| `compute_filament_velocity` | `computeFilamentVelocity` |
| `compute_regularized_mutual_velocity` | `computeRegularizedMutualVelocity` |
| `rk4_step` | `rk4Step` |
| `estimate_cfl_dt` | `estimateCflDt` |
| `guard_topology_step` | `guardTopologyStep` |
| `compute_intrinsic_frame` | `computeIntrinsicFrame` |
| `compute_rigid_motion` | `computeRigidMotion` |

Bindings: `src/vortexlab_kernels_py.cpp`, `src/vortexlab_kernels_node.cpp`.

Tests: `tests/test_vortexlab_kernels.py` (circle reach, two-circle inter, Hopf Gauss, velocity/RK4 smoke, frame/rigid).

## Capability flags (`getCapabilities`)

All VortexLab migration flags set `true` after K2–K5 land with tests.

## Follow-ups (not K0–K5)

- Workbench M1 `sstcore-adapter` / `require('sst-core')` wiring
- Workbench M2 JS domain-split (parallel plan)
- P2: mutual friction, background wall, BEM, stretch profiles
- Deeper Ideal/KnotPlot catalog golden fixtures beyond analytic circles
