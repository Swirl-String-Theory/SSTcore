# SST-Coil Digital Twin v4

Research-tool status: classical EM/circuit approximation. This suite does **not** prove gravity manipulation. It tests whether a SawShape 3-phase coil can produce an effective response that scales with `f0*R` after PWM, copper losses, approximate RL impedance, 3-phase phase shifts, SawShape geometry, and Biot-Savart projection.

## Main commands

```bash
python SST_Coil_90_RunAll.py
```

Run only the effective-kernel sweep:

```bash
python SST_Coil_80_ExtractEffectiveKernel.py --radii 0.03 0.05 0.10 --f-min 1e5 --f-max 8e6 --samples 70 --harmonics 9 --grid 13 --observable weighted_gradB2
```

For a faster smoke test:

```bash
python SST_Coil_80_ExtractEffectiveKernel.py --samples 25 --harmonics 5 --grid 9
```

## Outputs

All exports are written to:

```text
exports/SST-Coil/run_YYYYMMDD_HHMMSS/
    figures/
    csv/
    reports/
```

Key files:

- `figures/SST-Coil_effective_kernel_vs_frequency.png`
- `figures/SST-Coil_effective_kernel_fR_collapse.png`
- `csv/SST-Coil_effective_kernel_response.csv`
- `csv/SST-Coil_effective_kernel_features.csv`
- `reports/effective_kernel_summary.json`

## Interpretation

If curves align in `f0*R` rather than absolute `f0`, the digital-twin observable has geometry-kernel-like scaling. This is a necessary filter check only. Compare against measured data and against ordinary RLC/parasitic resonances before any SST interpretation.
