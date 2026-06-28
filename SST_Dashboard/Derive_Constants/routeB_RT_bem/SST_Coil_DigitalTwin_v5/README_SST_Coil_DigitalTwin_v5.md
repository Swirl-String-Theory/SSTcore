# SST-Coil Digital Twin v5

This version rebuilds the geometry from the user-supplied SawBowl / double-star / Rodin scripts instead of using the simplified ring-like geometry from earlier drafts.

Key points:

- `S=40`, `step_fwd=+11`, `step_bwd=-9` SawShape slot walk.
- 3 mechanical phase offsets: `0`, `2*pi/3`, `4*pi/3`.
- Bowl-compatible radius profiles: `constant`, `exponential`, `inverse_exp`, `linear`.
- `chord` mode preserves straight star segments; `curved_arc` is available for rounded visualizations.
- Current model is **distributed-lite**: PWM Fourier coefficients, skin-effect AC resistance, crude loop inductance, MOSFET Rds(on), deadtime envelope, phase shifts.
- Field model is Biot-Savart from the actual 3D polylines.

Run:

```bash
python SST_Coil_90_RunAll.py
```

Or:

```bash
python SST_Coil_80_ExtractEffectiveKernel_v5.py --samples 80 --harmonics 9 --grid 13 --height 0.006 --path-mode chord
```

Outputs go to:

```text
exports/SST-Coil/run_YYYYMMDD_HHMMSS/
```

Important output files:

```text
figures/SST-Coil_v5_geometry_user_sawshape.png
figures/SST-Coil_v5_effective_kernel_vs_frequency.png
figures/SST-Coil_v5_effective_kernel_fR_collapse.png
csv/SST-Coil_v5_effective_kernel_response.csv
csv/SST-Coil_v5_circuit_samples.csv
reports/SST-Coil_v5_summary.json
```

Research status: classical EM/circuit approximation only. It does not prove gravitational coupling.
