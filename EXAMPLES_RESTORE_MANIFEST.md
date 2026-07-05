# SSTcore examples restore manifest

Move-only restore from SST-Workbench to `SSTcore/examples/`.

## Restore to SSTcore/examples/

### example_*.py (19)
- example_ab_initio.py, example_biot_savart.py, example_enstrophy_circulation.py
- example_fetching_knots.py, example_fluid_rotation.py, example_fremlin_4_1_showcase.py
- example_golden_nls.py, example_heavy_knot.py, example_ideal_knot_showcase.py
- example_knot_visualization.py, example_magnus_integrator.py, example_particle_zoo_eval.py
- example_potential_flow.py, example_radiation_flow.py, example_relative_vorticity.py
- example_sst_gravity.py, example_sst_integrator.py, example_vortex_ring.py
- example_vorticity_transport.py

### API/support
- sstcore_resource_helpers.py, export_sstcore_resources.py
- fourier_knot.example.py, showcase_ideal_txt_figure8.py, biot-savart_on_fseries.py
- sstBindings.py, inspectSSTfunctions.py, knot_pd_and_volume_example.py
- test_ab_initio.py
- trefoil.py, trefoil_fields.py, trefoil_field_lines.py, taiChiTesting.py

### node_examples/
- Entire directory (+ README.md, tsconfig.json)

### Optional
- output/ (generated artifacts if present)

## Stays in Workbench/proof-scripts/sstcore/examples/
- knots.py, helicity2.py, HelicityCalculation.py, knots-toggle-autoknot.py
- braid_search_engine.py, braid_generator.py, braid_search_log.txt
- search_particles.py, eval_ab_initio.py
- investigate_knots.py, investigate_no_knotinfo.py
- hydrogen_spectrum_simulator.py, get_energy_rankine_core.py
- taichi_swirl_particles.py, wave_analysis.py, sphSimulator.py
- neonKnot.6_2.py, knot_6_2.py, VorticityExample.py
