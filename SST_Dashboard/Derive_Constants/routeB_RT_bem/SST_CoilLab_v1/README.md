# SST_CoilLab_v1

Clean research platform for the SST 3-phase coil work. This replaces the v10-style monolithic scripts with a package structure that keeps geometry, physics, experiments, and visualization separate.

## Hard rule

Every physical observable in the comparison pipeline must come from a Biot--Savart field map:

```python
segments = geometry.lanes
B = biot_savart(segments, currents)
observable = compute_from_B(B)
```

No imposed `sinc`, fake `exp(-f/fc)`, or geometry-independent response kernel is used to compare SawBowl and Rodin geometries.

## Geometry sectors

- `geometry/sawbowl.py`: exact logic from `GUI-SawBowl.py`: `S=40`, steps `+11,-9`, 3 phases, continuous `z(s)` and `r(s)`. No flat layer replication.
- `geometry/rodin6lane.py`: exact intent from `rodin_6lane_channel_guide_knot512.py`: `(P,Q)=(5,12)`, phase offsets `[0,1/3,2/3]` of one `q=12` sector, mirrored lanes via `z -> -z`, total 6 lanes.

Original scripts are preserved in `original_sources/`.

## Run

Quick sanity run:

```bash
python run_all.py --quick
```

Fuller run:

```bash
python run_all.py
```

Validation only:

```bash
python validate.py
```

Outputs are written to:

```text
exports/SST-CoilLab/run_YYYYMMDD_HHMMSS/
```

## Main outputs

- `reports/geometry_validation_*.json`
- `csv/geometry_compare_static_field.csv`
- `csv/frequency_sweep_field_observable.csv`
- `csv/radius_sweep_field_observable.csv`
- `csv/kernel_like_extracted_from_field_output.csv`
- `figures/geometry_*.png`
- `figures/Bmag_midplane_*.png`
- `figures/gradB2_midplane_*.png`
- `figures/frequency_sweep_absolute.png`
- `figures/frequency_sweep_normalized.png`
- `figures/radius_sweep_fR_*.png`
- `figures/kernel_like_fR_from_field_output.png`

## Interpretation discipline

If SawBowl and Rodin produce identical field maps or identical unnormalised observables, treat that as a bug. If normalized curves look similar, inspect the absolute CSV values and field maps first; normalization can hide geometry differences.
