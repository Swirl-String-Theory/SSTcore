# BEMv14 multigrid report

This wrapper runs BEMv14 over multiple independent grid families.

## Why this matters

A single grid can only show intra-family stability. Multiple grids test whether the same normalizer and blind budget survive across independent discretization choices.

## Per-grid selected normalizers

- `D1_ultra_paired_48_64_80`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15528054470374`, CV `7.553630911815354e-06`
- `D2_ultra_outer_anchored`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15451471285763`, CV `6.606870193078494e-07`
- `D3_ultra_tube_anchored`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.1549084854783`, CV `7.702478743874532e-06`

## Cross-grid consensus

- `M_Lcert2`: selected by `3` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `5.894392513597223e-06`

## Files

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`