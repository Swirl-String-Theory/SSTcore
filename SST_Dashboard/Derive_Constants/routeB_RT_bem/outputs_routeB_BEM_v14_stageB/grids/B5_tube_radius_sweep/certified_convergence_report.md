# BEMv14 certified-length convergence report

This report is alpha-blind: it does not contain or compare with observed fine structure.

BEMv14 tests whether the BEMv13 certified-length budget remains stable under mesh/tube/outer-boundary refinement.

The tested budget is

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm cert}
+\Delta F_{\rm pair}/\mathcal N_q\right].
\]

## Selected normalizer

- `normalizer`: `M_Lcert2`
- `n_runs`: `5`
- `n_valid`: `5`
- `pass_count`: `5`
- `pass_fraction`: `1.0`
- `alpha_inv_blind_v13_mean`: `137.15531387351444`
- `alpha_inv_blind_v13_std`: `0.00011134955601291714`
- `alpha_inv_blind_v13_span`: `0.0002656331656964994`
- `alpha_inv_blind_v13_cv_abs`: `8.118501053164039e-07`
- `abs_correction_ratio_mean`: `4.436374791295114e-06`
- `abs_correction_ratio_max`: `5.5334195130904184e-06`
- `DeltaF_phys_cert_mean`: `0.0012169393551221795`
- `DeltaF_phys_cert_std`: `0.00022269911202643514`
- `stability_gate`: `PASS_CERTIFIED_STABLE_NORMALIZER`

## Stability rule

- minimum grid runs: `3`
- `alpha_inv_blind_v13_cv_abs <= 0.01`
- `abs_correction_ratio_max <= 0.05`
- all runs must pass `PASS_SUBLEADING_CORRECTION`

No target alpha value is used.

## Interpretation

The selected normalizer passes the certified-length convergence grid. This is still not a final derivation; it requires analytic justification of the normalizer and independent provenance of \(N_{m soft}V_{m soft}\).

## Files

- `certified_convergence_grid.csv`
- `certified_stability_summary.csv`
- `alpha_budget_v14_convergence.csv`
- `runs/<run_id>/` if internal BEMv13 runs were launched