# VortexLab → SSTcore kernel implementation plan

One C++ source of truth; Python (`*_py.cpp`) and Node (`*_node.cpp`) are thin bindings.

## References

| Role | Path |
|------|------|
| Scientific authority | `SST-Workbench/GUI/vortexring-lab/vortexring-lab-v7.6.25b.html` |
| Byte-parity extract | `SST-Workbench/GUI/vortexlab-modular-v7.6.25b-m1/apps/web/src/legacy/vortexlab-runtime.js` |

## Binding rule

Each public kernel API ships in the same milestone with:

1. C++ header/source under `include/sst/` + `src/`
2. `CMakeLists.txt` / `setup.py` / `binding.gyp` registration
3. `*_py.cpp` + `*_node.cpp` + `module_sst.cpp` / `module_node.cpp`
4. `index.d.ts` + capability flag only when tests pass
5. `python scripts/gen_binding_manifest.py`

## API matrix

| API (Node camelCase) | C++ | Prior py/node | Gap | Fixture focus | atol / rtol |
|----------------------|-----|---------------|-----|---------------|-------------|
| `resampleClosedCurve` | `sst::curve::CurveSampling` | none | new | closed circle N→M | 1e-12 / 0 |
| `sampleCurve` | CurveSampling + Fourier | partial FourierKnot | unify | unit circle | 1e-10 / 0 |
| `loadKnotCatalog` / KnotPlot sample | `sst::catalog::KnotCatalog` | JS catalogs only | C++ catalog model | N300 metadata | — |
| `analyzeResolvedTube` (multi) | tube + clearance helpers | tube exists | multi-component witnesses | two rings | 1e-9 / 1e-8 |
| `computePolygonalGauss` | `PolygonalGaussInvariants` | legacy KnotDynamics | algorithm mismatch | Hopf / torus_6.9 Lk | 1e-8 / 1e-6 |
| `computeContinuousReach` | `ContinuousReachSolver` | proxy only | new | circle=1; two circles 0.4; ε⊥&lt;1e-8 | per-gate |
| `computeFilamentVelocity` | `FilamentVelocitySolver` | BiotSavart primitive | VL semantics | single ring LIA+BS | 1e-8 / 1e-5 |
| `computeRegularizedMutualVelocity` | same | — | new | mutual a_sim | 1e-8 / 1e-5 |
| `rk4Step` / `estimateCflDt` | `FilamentIntegrator` | Euler / Frenet RK4 | not drop-in | one step smoke | 1e-10 / 0 |
| `computeTopologyClearance` / `guardTopologyStep` | `TopologyGuard` | — | new | contact threshold | 1e-9 / 0 |
| `computeIntrinsicFrame` | `IntrinsicFrame` | — | new | PCA axes | 1e-10 / 0 |
| `computeRigidMotion` | `RigidMotionDecomposition` | — | new | rigid field residual | 1e-8 / 1e-6 |

Parity check: `abs(a-b) <= atol + rtol * max(|a|,|b|)`.

## Namespace layout

- `src/vortexlab/types.h` — shared structs/enums
- `sst::curve`, `sst::catalog`, `sst::knot`, `sst::geometry`, `sst::filament`, `sst::topology`, `sst::analysis`

## Out of scope

UI, Shapley, BEM, mutual friction, background wall, Workbench adapter wiring, npm publish.
