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
- `n_runs`: `3`
- `n_valid`: `3`
- `pass_count`: `3`
- `pass_fraction`: `1.0`
- `alpha_inv_blind_v13_mean`: `137.15422152203124`
- `alpha_inv_blind_v13_std`: `0.0013982418404174868`
- `alpha_inv_blind_v13_span`: `0.0026864076340302745`
- `alpha_inv_blind_v13_cv_abs`: `1.0194668635794675e-05`
- `abs_correction_ratio_mean`: `6.6148182905192785e-06`
- `abs_correction_ratio_max`: `1.4956469451917866e-05`
- `DeltaF_phys_cert_mean`: `-0.0009677636112560211`
- `DeltaF_phys_cert_std`: `0.002796483680827675`
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