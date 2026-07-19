# SSTcore binding coverage (C++ / Python / Node)

Layout convention for flat modules under `src/`:

```text
Foo.cpp + Foo.h + Foo_py.cpp + Foo_node.cpp
```

- Entry points: `module_sst.cpp` (Python), `module_node.cpp` (N-API)
- Shared helpers: `node_utils.h`
- Tube Python bind lives at `src/tube/geometry_py.cpp` (no Node twin yet)
- Side-by-side demos: `examples/example_*.py` + `examples/example_*.ts` (see `examples/README.md`)
- Regenerate machine-readable summary: `python scripts/gen_binding_manifest.py`

Legend: **Y** present · **—** absent · **via** exposed only through another bind module

## Flat modules

| Module | C++ | Python | Node |
|--------|-----|--------|------|
| ab_initio_mass | Y | Y | Y |
| atomic_bridge_model | Y | Y | — |
| biot_savart | Y | Y | Y |
| canonical_constants | Y | Y | — |
| chronos_kelvin_transport | Y | Y | — |
| clock_field_eft | Y | Y | — |
| delay_mode_selector | Y | Y | — |
| field_kernels | Y | Y | Y |
| field_ops | — (bind-only) | Y | Y |
| fluid_dynamics | Y | Y | Y |
| frenet_helicity | Y | Y | Y |
| hyperbolic_volume | Y | Y | Y |
| knot_dynamics | Y (+ `src/knot/*`) | Y | Y |
| magnus_integrator | Y | Y | Y |
| multisector_fitter | Y | Y | — |
| potential_timefield | Y | Y | Y |
| radiation_flow | Y | Y | Y |
| spectroscopic_gap | Y | Y | — |
| sst_extensions | Y | Y | Y |
| sst_gravity | Y | Y | Y |
| sst_integrator | Y | Y | Y |
| sst_master_equation | Y | Y | — |
| sst_tension_scales | Y | Y | — |
| swirl_field | Y | Y | Y |
| thermo_dynamics | Y | Y | Y |
| time_evolution | Y | Y | Y |
| trefoil_operator | Y | Y | — |
| trefoil_closure_kernels | Y | via biot_savart | via biot_savart |
| vortex_ring | Y | Y | Y |
| vorticity_dynamics | Y | Y | Y |

## Subsystems

| Area | C++ | Python | Node |
|------|-----|--------|------|
| knot parsers / invariants | `src/knot/*` | via `knot_dynamics_py.cpp` | via `knot_dynamics_node.cpp` |
| particle models | `src/particle/*` | via `ab_initio_mass_py.cpp` | via `ab_initio_mass_node.cpp` |
| filament | `src/filament/*` | via knot / extensions | via knot / integrator |
| resolved tube | `src/tube/*` | `tube/geometry_py.cpp` | — |

## Python-only gaps (no `*_node.cpp`)

- atomic_bridge_model
- canonical_constants
- chronos_kelvin_transport
- clock_field_eft
- delay_mode_selector
- multisector_fitter
- spectroscopic_gap
- sst_master_equation
- sst_tension_scales
- trefoil_operator
- resolved_tube_geometry (`src/tube/geometry_py.cpp`)

See also `docs/VORTEXLAB_NODE_CAPABILITIES.md` for VortexLab-oriented capability notes.
