# Blind BEMv10 normalizer-convergence report

This report is alpha-blind: it does not contain or compare with observed alpha.

BEMv10 tests whether a BEMv9 finite-correction normalizer remains stable under mesh/tube/outer-boundary refinement.

## Selected normalizer

- `normalizer`: `M_L2`
- `n_runs`: `1`
- `n_valid`: `1`
- `pass_count`: `1`
- `pass_fraction`: `1.0`
- `alpha_inv_blind_mean`: `137.15419109321292`
- `alpha_inv_blind_std`: `0.0`
- `alpha_inv_blind_span`: `0.0`
- `alpha_inv_blind_cv_abs`: `0.0`
- `abs_correction_ratio_mean`: `5.32195466024321e-05`
- `abs_correction_ratio_max`: `5.32195466024321e-05`
- `DeltaF_phys_mean`: `-0.014599344699713857`
- `DeltaF_phys_std`: `0.0`
- `stability_gate`: `FAIL_NOT_ENOUGH_GRID`

## Stability rule

- minimum grid runs: `3`
- `alpha_inv_blind_cv_abs <= 0.01`
- `abs_correction_ratio_max <= 0.05`
- all runs must pass `PASS_SUBLEADING_CORRECTION`

No target alpha value is used.

## Interpretation

The selected normalizer is only diagnostic because the supplied/reused grid is too small.

## Files

- `normalizer_convergence_grid.csv`
- `normalizer_stability_summary.csv`
- `alpha_budget_v10_convergence.csv`
- `runs/<run_id>/` if internal BEMv9 runs were launched