# Node / TypeScript examples (SSTcore N-API)

These scripts mirror the **intent** of the Python files under `examples/`, but call the **native addon** loaded from the repo root (`require('../index.js')`).

## Run

From the SSTcore repo root (after `npm run build:node`):

```bash
npx tsx node_examples/biot_savart.example.ts
npm run examples:node:all
```

## Mapping: Python → TypeScript (by `src/node/node_*.cpp`)

| C++ binding | TypeScript | Python reference |
|-------------|------------|------------------|
| `node_biot_savart.cpp` | `biot_savart.example.ts` | `example_biot_savart.py`, `biot-savart_on_fseries.py` |
| `node_fluid_dynamics.cpp` | `fluid_dynamics.example.ts` | `example_fluid_rotation.py` |
| `node_frenet_helicity.cpp` | `frenet_helicity.example.ts` | `HelicityCalculation.py` |
| `node_field_kernels.cpp` | `field_kernels.example.ts` | (minimal grid sanity) |
| `node_field_ops.cpp` | `field_ops.example.ts` | (curl / grid ops) |
| `node_knot.cpp` | `knot.example.ts` | knot / f-series examples |
| `node_potential_timefield.cpp` | `potential_timefield.example.ts` | `example_potential_flow.py` |
| `node_hyperbolic_volume.cpp` | `hyperbolic_volume.example.ts` | `knot_pd_and_volume_example.py` |
| `node_radiation_flow.cpp` | `radiation_flow.example.ts` | `example_radiation_flow.py` |
| `node_swirl_field.cpp` | `swirl_field.example.ts` | trefoil-related examples |
| `node_thermo_dynamics.cpp` | `thermo_dynamics.example.ts` | (thermo helpers) |
| `node_time_evolution.cpp` | `time_evolution.example.ts` | time-step demos |
| `node_vortex_ring.cpp` | `vortex_ring.example.ts` | `example_vortex_ring.py` |
| `node_vorticity_dynamics.cpp` | `vorticity_dynamics.example.ts` | `example_vorticity_transport.py` |
| `node_sst_gravity.cpp` | `sst_gravity.example.ts` | `example_sst_gravity.py` |
| `node_sst_extensions.cpp` | `sst_extensions.example.ts` | f-series / helicity extensions |
| `node_ab_initio.cpp` | `ab_initio.example.ts` | `example_ab_initio.py` (if present) / particle zoo |
| `node_sst_integrator.cpp` | `sst_integrator.example.ts` | mass integrator |
| `node_magnus_integrator.cpp` | `magnus_integrator.example.ts` | Magnus / swirl Coulomb |

If a binding is still a stub, the example prints `[SKIP]` and exits 0 so the folder stays complete for CI.
