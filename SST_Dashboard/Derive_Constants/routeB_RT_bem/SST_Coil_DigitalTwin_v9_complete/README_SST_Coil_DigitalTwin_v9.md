# SST-Coil Digital Twin v9 — Complete Research Package

This package consolidates the previous sliced v1–v8 work into one consistent research suite.

## Design rule

The package keeps the two geometry sectors separate:

1. **SawBowl / SawShape sector**
   - Source logic: `original_sources/GUI-SawBowl.py`
   - `S=40`, steps `(+11,-9)`
   - continuous `z` and `r` progression along the wire
   - three phase offsets `[0, 120°, 240°]`

2. **Rodin 6-lane torus-knot sector**
   - Source logic: `original_sources/rodin_6lane_channel_guide_knot512.py`
   - `(p,q)=(5,12)` torus-knot lanes
   - phase cell offsets `[0, 1/3, 2/3]` of one `q=12` sector
   - mirrored counterpart by `z -> -z`
   - total 6 continuous lanes

These sectors are intentionally not mixed.

## Files

```text
SST_Coil_00_common.py                 constants, run dirs, summaries
SST_Coil_01_plotting.py               reusable plotting helpers
SST_Coil_10_geometry_sawbowl.py       exact SawBowl/SawShape geometry sector
SST_Coil_11_geometry_rodin6lane.py    exact Rodin 6-lane torus-knot sector
SST_Coil_20_winding_factors.py        S=40 analytic winding/phase tables
SST_Coil_30_pwm_current.py            PWM harmonic + copper/RL current model
SST_Coil_40_biot_savart.py            Biot-Savart solver
SST_Coil_50_observables.py            B, pressure, grad(B^2) diagnostics
SST_Coil_60_radius_scaling.py         fR/radius-scaling sweeps from digital twin
SST_Coil_80_compare_geometries.py     geometry comparison + static diagnostics
SST_Coil_90_RunAll.py                 quick full pipeline
SST_Coil_99_validate.py               sanity validation
original_sources/                     untouched user scripts used as references
docs/PATCH_NOTES.diff                 summary diff/changelog from v8 to v9
```

## Quick run

```bash
python SST_Coil_99_validate.py
python SST_Coil_90_RunAll.py
```

Outputs go to:

```text
exports/SST-Coil/run_YYYYMMDD_HHMMSS/
```

## High-resolution examples

```bash
python SST_Coil_80_compare_geometries.py --grid 21
python SST_Coil_60_radius_scaling.py --geometry sawbowl --samples 80 --grid 11 --harmonics 7 --f-min 1e5 --f-max 10e6
python SST_Coil_60_radius_scaling.py --geometry rodin --samples 80 --grid 11 --harmonics 7 --f-min 1e5 --f-max 10e6
```

## Current physics status

This is a classical electromagnetic and geometry digital twin. It can test:

- whether response features follow `fR = constant`,
- whether SawBowl and Rodin geometries differ under the same drive,
- whether ordinary PWM/copper/RL effects dominate,
- whether a candidate kernel emerges from geometry rather than being imposed.

It does **not** prove SST gravitational coupling or anomalous lift. Those remain research-track hypotheses requiring laboratory comparison.
