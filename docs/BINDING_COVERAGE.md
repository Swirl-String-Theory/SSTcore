# SSTcore binding coverage (C++ / Python / Node)

Layout convention for flat modules under `src/`:

```text
Foo.cpp + Foo.h + Foo_py.cpp + Foo_node.cpp
```

- Entry points: `module_sst.cpp` (Python), `module_node.cpp` (N-API)
- Shared helpers: `node_utils.h`
- Tube binds: `src/tube/geometry_py.cpp` + `src/tube/geometry_node.cpp`
- Side-by-side demos: `examples/example_*.py` + `examples/example_*.ts` (see `examples/README.md`)
- Regenerate machine-readable summary: `python scripts/gen_binding_manifest.py`

Legend: **Y** present · **—** absent · **via** exposed only through another bind module

## Flat modules

| Module | C++ | Python | Node |
|--------|-----|--------|------|
| ab_initio_mass | Y | Y | Y |
| atomic_bridge_model | Y | Y | Y |
| biot_savart | Y | Y | Y |
| canonical_constants | Y | Y | Y |
| chronos_kelvin_transport | Y | Y | Y |
| clock_field_eft | Y | Y | Y |
| delay_mode_selector | Y | Y | Y |
| field_kernels | Y | Y | Y |
| field_ops | — (bind-only) | Y | Y |
| fluid_dynamics | Y | Y | Y |
| frenet_helicity | Y | Y | Y |
| hyperbolic_volume | Y | Y | Y |
| knot_dynamics | Y (+ `src/knot/*`) | Y | Y |
| magnus_integrator | Y | Y | Y |
| multisector_fitter | Y | Y | Y |
| potential_timefield | Y | Y | Y |
| radiation_flow | Y | Y | Y |
| spectroscopic_gap | Y | Y | Y |
| sst_extensions | Y | Y | Y |
| sst_gravity | Y | Y | Y |
| sst_integrator | Y | Y | Y |
| sst_master_equation | Y | Y | Y |
| sst_tension_scales | Y | Y | Y |
| swirl_field | Y | Y | Y |
| thermo_dynamics | Y | Y | Y |
| time_evolution | Y | Y | Y |
| trefoil_operator | Y | Y | Y |
| trefoil_closure_kernels | Y | via biot_savart | via biot_savart |
| vortex_ring | Y | Y | Y |
| vorticity_dynamics | Y | Y | Y |

## Subsystems

| Area | C++ | Python | Node |
|------|-----|--------|------|
| knot parsers / invariants | `src/knot/*` | via `knot_dynamics_py.cpp` | via `knot_dynamics_node.cpp` |
| particle models | `src/particle/*` | via `ab_initio_mass_py.cpp` | via `ab_initio_mass_node.cpp` |
| filament | `src/filament/*` + VortexLab velocity/integrator | `filament_*_py.cpp` | `filament_*_node.cpp` |
| resolved tube | `src/tube/*` | `tube/geometry_py.cpp` | `tube/geometry_node.cpp` |
| VortexLab geometry/reach/analysis | `src/curve|geometry|topology|analysis|catalog|knot/polygonal_gauss*` | matching `*_py.cpp` | matching `*_node.cpp` |

## Remaining py-only (historical)

- `resolved_tube_geometry` pure Python helpers outside native binds (if any)
- See `resources/binding_manifest.json` (`py_only_modules`) after `gen_binding_manifest.py`

See also `docs/VORTEXLAB_NODE_CAPABILITIES.md` and `docs/VORTEXLAB_KERNEL_STATUS.md`.
