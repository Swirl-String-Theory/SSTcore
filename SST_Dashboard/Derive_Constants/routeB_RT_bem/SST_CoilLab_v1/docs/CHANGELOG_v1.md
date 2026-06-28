# Changelog v1

- Replaced version-chain patching with clean package `SST_CoilLab_v1`.
- Preserved original source scripts unchanged in `original_sources/`.
- Added strict separation of SawBowl and Rodin6lane geometry sectors.
- Implemented Biot--Savart as the only source of magnetic field maps.
- Added geometry validation gates: SawBowl 3 lanes with monotonic continuous z; Rodin6lane 6 lanes with mirror rule z -> -z.
- Added geometry comparison, PWM comparison, frequency sweep, radius sweep, and kernel-like extraction from field-derived observables.
- Removed fake kernel assumptions from geometry comparison.
