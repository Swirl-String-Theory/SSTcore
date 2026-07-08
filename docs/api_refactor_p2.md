# SSTcore API refactor — Prioriteit 2 (v0.8.18+)

## Completed in P2

### Tube internal split (`p2-tube-split`)

| Module | Header | Implementation |
|--------|--------|----------------|
| Core geometry | `include/sst/tube/geometry_core.h` | `src/tube/geometry_core.cpp` |
| Rigidity matrix | `include/sst/tube/rigidity_matrix.h` | `src/tube/rigidity_matrix.cpp` |
| NNLS solvers | `include/sst/tube/nnls.h` | `src/tube/nnls.cpp` |
| Matrix Market I/O | `include/sst/tube/io.h` | `src/tube/io.cpp` |
| Contact stress | `include/sst/tube/contact_stress.h` | `src/tube/contact_stress.cpp` |
| Tightener | `include/sst/tube/tightener.h` | `src/tube/tightener.cpp` |
| Shared helpers | `include/sst/tube/detail/common.h` | `src/tube/detail/common.cpp` |

- Umbrella: `include/sst/tube/geometry.h`, `include/sst/tube.h`
- Shim: `src/resolved_tube_geometry.h`
- `ContactStressMap` retains deprecated static forwards to free functions

### Spectral split (`p2-spectral`)

Headers under `include/sst/spectral/`:

- `grid1d.h` — grid and potential option structs, `SpectralResult`
- `finite_difference.h` — `sst::spectral::build_*` FD helpers
- `potential_builder.h`
- `dense_linalg.h`
- `eigensolver_jacobi.h`
- `diagnostics.h`
- `trefoil_operator.h` — `TrefoilOperator` inline forwards + combined solvers

Façade: `include/sst/spectral.h`  
Shim: `src/trefoil_operator.h`  
Implementation: `src/trefoil_operator.cpp` (`sst::spectral::` + `TrefoilOperator::buildAndSolve*`)

### Fusions (`p2-fusions`)

**Filament** — `include/sst/filament/evolution.h`, `src/filament/evolution.cpp`

- `FilamentEvolution` merges `TimeEvolution` + `VortexKnotSystem` logic
- Factories: `make_trefoil`, `make_figure8`, `make_from_fseries`
- `TimeEvolution` and `VortexKnotSystem` are deprecated wrappers

**Continuum** — `include/sst/continuum/{vorticity,thermo,radiation}.h`

- Free functions in `sst::continuum::{vorticity,thermo,radiation}`
- `src/{vorticity_dynamics,thermo_dynamics,radiation_flow}.h` are deprecated shims

**Clock** — `include/sst/clock/`

- `swirl_clock.h` — `factor_from_speed`, `map_from_velocity_field`
- `kelvin.h`, `delay.h`, `timefield.h`, `eft.h` — shims to existing `src/` headers
- Umbrella: `include/sst/clock.h`
- `SSTGravity::compute_swirl_clock` delegates to `clock::map_from_velocity_field`

**Particle** — `include/sst/particle/{scales,atomic}.h`

- Implementations in `sst_tension_scales.cpp`, `spectroscopic_gap.cpp`, `atomic_bridge_model.cpp`
- `SSTTensionScales`, `SpectroscopicGap`, `AtomicBridgeModel` are deprecated class forwards

**Multisector** — `include/sst/fitting/{multisector,nodes,trace}.h`

- `MultisectorFitterV2` is the implementation
- `MultisectorFitter` delegates to V2 (deprecated)
- `src/multisector_fitter.h` shim includes `sst/fitting/multisector.h`

### Facades (`p2-facades`)

| Umbrella | Contents |
|----------|----------|
| `include/sst/field.h` | biot_savart, field_kernels, frenet_helicity |
| `include/sst/continuum.h` | vorticity, thermo, radiation |
| `include/sst/clock.h` | swirl clock + kelvin/delay/timefield/eft |
| `include/sst/fitting.h` | multisector, nodes, trace |
| `include/sst/filament.h` | evolution, vortex_knot_system |

### Build / tests (`p2-tests`)

- `CMakeLists.txt` and `setup.py` list split tube `.cpp` files + `filament/evolution.cpp`
- Tests: `test_resolved_tube_geometry`, `test_frenet`, `test_sst_integrator`

## Dependency rules (unchanged from P1)

```
FourierBlock → centerline (Vec3[]) → tube::analyze → KnotInvariants tube fields
```

Tube does not depend on knot. Spectral and fitting are header-only splits over existing `src/` implementations.

## Next: P3

- Python submodules in `module_sst.cpp`
- Flat backwards-compat wrappers with `DeprecationWarning`
- See `api_refactor_p1.md`
