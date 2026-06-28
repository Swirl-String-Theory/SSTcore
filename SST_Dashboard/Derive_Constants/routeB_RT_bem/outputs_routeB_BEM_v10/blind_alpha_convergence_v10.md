# Blind BEMv10 normalizer-convergence report

This report is alpha-blind: it does not contain or compare with observed alpha.

BEMv10 tests whether a BEMv9 finite-correction normalizer remains stable under mesh/tube/outer-boundary refinement.

## Selected normalizer

- `normalizer`: `M_L2`
- `n_runs`: `4`
- `n_valid`: `4`
- `pass_count`: `4`
- `pass_fraction`: `1.0`
- `alpha_inv_blind_mean`: `137.16166823004758`
- `alpha_inv_blind_std`: `0.000983071129691701`
- `alpha_inv_blind_span`: `0.002110181276947287`
- `alpha_inv_blind_cv_abs`: `7.167243898221578e-06`
- `abs_correction_ratio_mean`: `5.0693597579197394e-06`
- `abs_correction_ratio_max`: `1.112453487601376e-05`
- `DeltaF_phys_mean`: `0.00013521601271929856`
- `DeltaF_phys_std`: `0.0019661422593697194`
- `stability_gate`: `PASS_STABLE_NORMALIZER`

## Stability rule

- minimum grid runs: `3`
- `alpha_inv_blind_cv_abs <= 0.01`
- `abs_correction_ratio_max <= 0.05`
- all runs must pass `PASS_SUBLEADING_CORRECTION`

No target alpha value is used.

## Interpretation

The selected normalizer passes this convergence grid. This is still not a derivation; it needs a larger grid and analytic justification.

## Files

- `normalizer_convergence_grid.csv`
- `normalizer_stability_summary.csv`
- `alpha_budget_v10_convergence.csv`
- `runs/<run_id>/` if internal BEMv9 runs were launched