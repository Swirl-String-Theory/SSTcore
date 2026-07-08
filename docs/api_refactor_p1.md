# SSTcore API refactor — Prioriteit 1 (v0.8.18)

## Completed in P1

### Central types
- Canonical `Vec3` / `Vec2f` in [`include/sst/types.h`](../include/sst/types.h)
- [`include/vec3_utils.h`](../include/vec3_utils.h) is a compatibility shim

### Canon single-route
- [`include/sst/constants.h`](../include/sst/constants.h): `SSTMassScaleContext`
- Hardcoded `c` / `rho_f` removed from core headers and pybind defaults
- `MassFunctional::baseline_mass_from_horn_ropelength` delegates to `SSTMasterEquation::geometric_horn_baseline_mass`

### Tube domain (`sst::tube`)
- Types: [`include/sst/tube/types.h`](../include/sst/tube/types.h)
- API: [`include/sst/tube/geometry.h`](../include/sst/tube/geometry.h)
- Façade: [`include/sst/tube.h`](../include/sst/tube.h)
- Implementation: [`src/tube/geometry.cpp`](../src/tube/geometry.cpp)
- Shim: [`src/resolved_tube_geometry.h`](../src/resolved_tube_geometry.h)

### Knot → tube bridge
- [`include/sst/knot/invariants_bridge.h`](../include/sst/knot/invariants_bridge.h)
- [`src/knot/invariants_bridge.cpp`](../src/knot/invariants_bridge.cpp)
- `knot_dynamics.cpp` no longer includes tube headers directly

### Workbench façade
- [`include/sst/workbench/extensions.h`](../include/sst/workbench/extensions.h)
- [`src/sst_extensions.h`](../src/sst_extensions.h) shim; `sstext` aliases `workbench`

### Python
- Flat API unchanged; [`SSTcore/__init__.py`](../src/SSTcore/__init__.py) has `_DEPRECATION_MAP` scaffold for P3

## Dependency rule

```
FourierBlock → centerline (Vec3[]) → tube::analyze → KnotInvariants tube fields
```

Tube does not depend on knot. Knot supplies points; tube analyzes geometry only.

## Next: P2

- Split `knot_dynamics.h/cpp` into `knot/`, `particle/`, `filament/`
- Internal split of `tube/` (nnls, io, tightener)
- See `sstcore_refactor_p2_*.plan.md`

## Next: P3

- Python submodules in `module_sst.cpp`
- Flat backwards-compat wrappers with `DeprecationWarning`
