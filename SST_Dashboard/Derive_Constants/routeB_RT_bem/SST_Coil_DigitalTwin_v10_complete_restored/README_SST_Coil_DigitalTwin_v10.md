# SST Coil Digital Twin v10 — complete restored research package

This package fixes the v9 regression where `RunAll` produced fewer research artifacts.

## What changed

- All historical source files supplied in `SST_Coil_all files.zip` are preserved under:
  `legacy_all_versions_from_user_zip/`
- Duplicate filenames from the zip are preserved with `__zipentryXX` suffixes.
- The active research pipeline remains in the package root with stable module names.
- `SST_Coil_90_RunAll.py` now creates one timestamped run folder and exports the broad set of artifacts again:
  geometry plots, winding factors, phase tables, current spectrum, static field diagnostics,
  Biot-Savart midplanes, radius-scaling sweeps, fR-collapse plots, and comparison CSVs.

## Run

```bash
python SST_Coil_90_RunAll.py
```

Optional quick mode:

```bash
python SST_Coil_90_RunAll.py --quick
```

Outputs go to:

```text
exports/SST-Coil/run_YYYYMMDD_HHMMSS/
```

## Geometry sectors

- SawBowl/SawShape: exact continuous-z/r logic derived from `GUI-SawBowl.py`.
- Rodin 6-lane torus: exact `(5,12)` guide with 3 phase lanes and mirrored `z -> -z` lanes,
  derived from `rodin_6lane_channel_guide_knot512.py`.

## Important

This is a classical EM + signal-processing research tool. It is not evidence of gravity manipulation.
It is designed to test whether geometry, PWM, copper/RL response, and observables show reproducible
scaling behavior worth comparing to experiment.
