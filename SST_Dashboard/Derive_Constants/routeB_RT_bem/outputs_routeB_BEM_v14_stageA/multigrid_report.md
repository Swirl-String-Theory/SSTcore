# BEMv14 multigrid report

This wrapper runs BEMv14 over multiple independent grid families.

## Why this matters

A single grid can only show intra-family stability. Multiple grids test whether the same normalizer and blind budget survive across independent discretization choices.

## Per-grid selected normalizers

- `A1_paired_micro_low`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.1501627420922`, CV `0.00010652182335624496`
- `A2_paired_micro_high`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.15905190345143`, CV `0.0001140956934088641`
- `A3_cartesian_tiny`: normalizer `M_Lcert2`, stability `PASS_CERTIFIED_STABLE_NORMALIZER`, mean `137.4354010172716`, CV `0.002974204054091488`

## Cross-grid consensus

- `M_Lcert2`: selected by `3` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `0.0028263191049214646`

## Files

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`