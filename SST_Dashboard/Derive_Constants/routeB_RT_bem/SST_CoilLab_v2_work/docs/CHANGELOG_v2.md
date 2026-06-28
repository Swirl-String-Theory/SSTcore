# SST_CoilLab v2 changelog

- Added geometry-derived 3x3 self/mutual phase inductance estimate.
- Added frequency-domain 3-phase RL mutual current solver.
- Added `mutual_frequency_sweep` experiment.
- `run_all.py` now writes:
  - `csv/mutual_L_matrix.csv`
  - `csv/mutual_phase_currents.csv`
  - `csv/mutual_frequency_sweep_field_observable.csv`
  - `figures/mutual_frequency_sweep_absolute.png`
  - `figures/mutual_frequency_sweep_normalized.png`
- Preserved v1 Biot--Savart rule: field observables still come from computed B maps.
