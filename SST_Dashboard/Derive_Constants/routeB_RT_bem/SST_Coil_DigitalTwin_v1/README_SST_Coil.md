# SST-Coil prefixed script suite

Purpose: non-GUI mathematical tests for SawShape / Rodin-like 3-phase coils.

This is a classical EM + Fourier/PWM + geometry-kernel diagnostic suite. It does **not** assume or prove gravity modification. It tests prerequisite structure: harmonic content, geometry selection, Biot-Savart fields, pressure/stress proxies, and `fR = constant` scaling.

## File naming

All Python files use the shared prefix `SST_Coil_` so they stay grouped next to other scripts:

```text
SST_Coil_00_common.py
SST_Coil_10_PWM_Spectrum.py
SST_Coil_20_Geometry_SawShape.py
SST_Coil_30_BiotSavart.py
SST_Coil_40_FieldAnalysis.py
SST_Coil_50_MaxwellStress.py
SST_Coil_60_FRScaling.py
SST_Coil_70_HarmonicScanner.py
SST_Coil_80_ParamSweep.py
SST_Coil_90_RunAll.py
```

## Exports

Everything exports to a separate timestamped folder:

```text
exports/SST-Coil/run_YYYYMMDD_HHMMSS/
    figures/
    csv/
    npz/
    reports/
    logs/
```

## Quick run

```bash
python SST_Coil_90_RunAll.py
```

## Recommended workflow

1. Run `SST_Coil_10_PWM_Spectrum.py` to compare duty cycles.
2. Run `SST_Coil_20_Geometry_SawShape.py` to inspect the path.
3. Run `SST_Coil_30_BiotSavart.py` for a harmonic field scan.
4. Run `SST_Coil_60_FRScaling.py` to generate candidate node frequencies.
5. Use `SST_Coil_70_HarmonicScanner.py` and `SST_Coil_80_ParamSweep.py` for test planning.

## Hard falsifier

If a measured anomaly is governed by a geometry kernel `G(kR)`, then comparable peaks/nodes should follow:

```text
f_opt * R_coil = constant
```

If peaks remain fixed in absolute frequency when radius changes, suspect ordinary electronics: LC resonance, parasitic capacitance, gate-driver artifacts, heating, mechanical vibration, or measurement coupling.


## v2 geometry correction

The SawShape geometry now defaults to `path_mode="chord"`, meaning each `+11,-9` step is drawn as a straight slot-to-slot segment. This is the correct star / saw path for the physical winding. The older arc interpolation can be requested with `--path-mode arc`, but with constant radius and zero height it collapses visually toward a simple ring and should not be used for the main SawShape tests.
