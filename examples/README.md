# SSTcore examples

Python demos and matching Node/TypeScript N-API demos live side by side:

```text
example_biot_savart.py
example_biot_savart.ts
```

TypeScript examples call the native addon from the repo root (`require('../index.js')`).

## Run (Node)

From the SSTcore repo root (after `npm run build:node`):

```bash
npx tsx examples/example_biot_savart.ts
npm run examples:node:all
```

## Mapping: binding → TypeScript / Python

| C++ binding | TypeScript | Python reference |
|-------------|------------|------------------|
| `biot_savart_node.cpp` | `example_biot_savart.ts` | `example_biot_savart.py`, `biot-savart_on_fseries.py` |
| `fluid_dynamics_node.cpp` | `example_fluid_rotation.ts` | `example_fluid_rotation.py` |
| `frenet_helicity_node.cpp` | `example_frenet_helicity.ts` | `example_frenet_helicity.py` |
| `field_kernels_node.cpp` | `example_field_kernels.ts` | `example_field_kernels.py` |
| `field_ops_node.cpp` | `example_field_ops.ts` | `example_field_ops.py` |
| `knot_dynamics_node.cpp` | `example_knot.ts` | knot / f-series examples |
| `potential_timefield_node.cpp` | `example_potential_flow.ts` | `example_potential_flow.py` |
| `hyperbolic_volume_node.cpp` | `example_hyperbolic_volume.ts` | `knot_pd_and_volume_example.py` |
| `radiation_flow_node.cpp` | `example_radiation_flow.ts` | `example_radiation_flow.py` |
| `swirl_field_node.cpp` | `example_swirl_field.ts` | `example_swirl_field.py` |
| `thermo_dynamics_node.cpp` | `example_thermo_dynamics.ts` | `example_thermo_dynamics.py` |
| `time_evolution_node.cpp` | `example_time_evolution.ts` | `example_time_evolution.py` |
| `vortex_ring_node.cpp` | `example_vortex_ring.ts` | `example_vortex_ring.py` |
| `vorticity_dynamics_node.cpp` | `example_vorticity_transport.ts` | `example_vorticity_transport.py` |
| `sst_gravity_node.cpp` | `example_sst_gravity.ts` | `example_sst_gravity.py` |
| `sst_extensions_node.cpp` | `example_sst_extensions.ts` | `example_sst_extensions.py` |
| `ab_initio_mass_node.cpp` | `example_ab_initio.ts` | `example_ab_initio.py` |
| `sst_integrator_node.cpp` | `example_sst_integrator.ts` | `example_sst_integrator.py` |
| `magnus_integrator_node.cpp` | `example_magnus_integrator.ts` | `example_magnus_integrator.py` |

If a binding is still a stub, the TypeScript example prints `[SKIP]` and exits 0.

Full C++ / Python / Node matrix: [`docs/BINDING_COVERAGE.md`](../docs/BINDING_COVERAGE.md).
