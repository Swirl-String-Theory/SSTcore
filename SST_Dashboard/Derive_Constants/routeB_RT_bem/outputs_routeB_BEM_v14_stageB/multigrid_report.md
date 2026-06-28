# BEMv14 multigrid report

This wrapper runs BEMv14 over multiple independent grid families.

## Why this matters

A single grid can only show intra-family stability. Multiple grids test whether the same normalizer and blind budget survive across independent discretization choices.

## Per-grid selected normalizers

- `B1_paired_coarse`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.16070678544918`, CV `4.920047531266853e-05`
- `B2_paired_medium`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15692869796575`, CV `2.1665515347271534e-05`
- `B3_cartesian_mesh_cross`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.18360773796144`, CV `0.0004494517427533972`
- `B4_outer_radius_sweep`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.1564871810404`, CV `8.963132576432184e-06`
- `B5_tube_radius_sweep`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15531387351444`, CV `8.118501053164039e-07`

## Cross-grid consensus

- `M_Lcert2`: selected by `5` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `0.0003698544154412709`

## Files

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`