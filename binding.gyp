{
  "targets": [
    {
      "target_name": "sstcore",
      "sources": [
        "src/module_node.cpp",
        "src/ab_initio_mass_node.cpp",
        "src/atomic_bridge_model_node.cpp",
        "src/biot_savart_node.cpp",
        "src/canonical_constants_node.cpp",
        "src/chronos_kelvin_transport_node.cpp",
        "src/clock_field_eft_node.cpp",
        "src/delay_mode_selector_node.cpp",
        "src/field_kernels_node.cpp",
        "src/field_ops_node.cpp",
        "src/fluid_dynamics_node.cpp",
        "src/frenet_helicity_node.cpp",
        "src/hyperbolic_volume_node.cpp",
        "src/knot_dynamics_node.cpp",
        "src/magnus_integrator_node.cpp",
        "src/multisector_fitter_node.cpp",
        "src/potential_timefield_node.cpp",
        "src/radiation_flow_node.cpp",
        "src/spectroscopic_gap_node.cpp",
        "src/trefoil_operator_node.cpp",
        "src/tube/geometry_node.cpp",
        "src/sst_extensions_node.cpp",
        "src/sst_gravity_node.cpp",
        "src/sst_integrator_node.cpp",
        "src/sst_master_equation_node.cpp",
        "src/sst_tension_scales_node.cpp",
        "src/swirl_field_node.cpp",
        "src/thermo_dynamics_node.cpp",
        "src/time_evolution_node.cpp",
        "src/vortex_ring_node.cpp",
        "src/vorticity_dynamics_node.cpp",
        "src/ab_initio_mass.cpp",
        "src/trefoil_closure_kernels.cpp",
        "src/biot_savart.cpp",
        "src/fluid_dynamics.cpp",
        "src/field_kernels.cpp",
        "src/frenet_helicity.cpp",
        "src/potential_timefield.cpp",
        "src/magnus_integrator.cpp",
        "src/multisector_fitter.cpp",
        "src/trefoil_operator.cpp",
        "src/tube/detail/common.cpp",
        "src/tube/geometry_core.cpp",
        "src/tube/rigidity_matrix.cpp",
        "src/tube/nnls.cpp",
        "src/tube/io.cpp",
        "src/tube/contact_stress.cpp",
        "src/tube/tightener.cpp",
        "src/hyperbolic_volume.cpp",
        "src/knot/resource_loader.cpp",
        "src/knot/fourier_parser.cpp",
        "src/knot/ideal_parser.cpp",
        "src/knot/fourier_eval.cpp",
        "src/knot/invariants.cpp",
        "src/knot/invariants_bridge.cpp",
        "src/particle/xi_model.cpp",
        "src/particle/mass_functional.cpp",
        "src/particle/knot_particle_model.cpp",
        "src/filament/vortex_knot_system.cpp",
        "src/filament/evolution.cpp",
        "src/radiation_flow.cpp",
        "src/swirl_field.cpp",
        "src/thermo_dynamics.cpp",
        "src/time_evolution.cpp",
        "src/vortex_ring.cpp",
        "src/vorticity_dynamics.cpp",
        "src/sst_gravity.cpp",
        "src/sst_extensions.cpp",
        "src/sst_integrator.cpp",
        "build_node/generated/knot_files_embedded.cpp"
      ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")",
        "src",
        "include",
        "include/generated",
        "<(module_root_dir)/build_node/generated"
      ],
      "defines": [
        "NAPI_DISABLE_CPP_EXCEPTIONS",
        "SSTCORE_NUMERIC_PROFILE=\"deterministic\""
      ],
      "cflags!": [ "-fno-exceptions" ],
      "cflags_cc!": [ "-fno-exceptions" ],
      "conditions": [
        ["OS=='win'", {
          "defines": [ "_CRT_SECURE_NO_WARNINGS" ],
          "msvs_settings": {
            "VCCLCompilerTool": {
              "ExceptionHandling": 1,
              "AdditionalOptions": [ "/std:c++20", "/bigobj", "/Zm2000", "/O2" ]
            }
          }
        }],
        ["OS=='mac'", {
          "cflags_cc": [ "-std=c++20", "-O2" ],
          "xcode_settings": {
            "OTHER_CPPFLAGS": [ "-std=c++20", "-O2" ],
            "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
            "OTHER_LDFLAGS": [ "-undefined", "dynamic_lookup" ]
          }
        }],
        ["OS=='linux'", {
          "cflags_cc": [ "-std=c++20", "-O2", "-fPIC" ]
        }]
      ]
    }
  ]
}
