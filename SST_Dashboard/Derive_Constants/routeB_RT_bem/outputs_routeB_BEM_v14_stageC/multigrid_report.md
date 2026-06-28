# BEMv14 multigrid report

This wrapper runs BEMv14 over multiple independent grid families.

## Why this matters

A single grid can only show intra-family stability. Multiple grids test whether the same normalizer and blind budget survive across independent discretization choices.

## Per-grid selected normalizers

- `C1_paired_fine`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15477301864115`, CV `7.168324914721296e-06`
- `C2_paired_fine_alt_tail`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.1552930828202`, CV `1.1767683718054626e-05`
- `C3_cartesian_fine_small`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15564493637547`, CV `1.3296040759420608e-05`
- `C4_tube_boundary_only`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15422152203124`, CV `1.0194668635794675e-05`
- `C5_sphere_boundary_only`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15470540383689`, CV `0.0`

## Cross-grid consensus

- `M_Lcert2`: selected by `5` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `1.2241728079540825e-05`

## Files

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`