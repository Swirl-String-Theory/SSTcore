# BEMv13 certified-length budget report

This report is alpha-blind: it does not contain or compare with observed fine structure.

BEMv13 uses the database `L` column as the certified longitudinal length, while the Fourier coefficients remain the BEM geometry source.

The working budget is

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm cert}(3_1)
+\Delta F_{\rm pair}/\mathcal N_q\right].
\]

## Selected candidate

- `target`: `7_1`
- `reference`: `0_1`
- `normalizer`: `M_Lcert2`
- `L_cert_target`: `30.700289`
- `NsoftV`: `16.755160819145562`
- `leading_full_cert`: `514.3882793892456`
- `leading_half_alpha_inv_cert`: `257.1941396946228`
- `DeltaF_pair_raw`: `353.1851437825582`
- `normalizer_denominator`: `202639.16510695702`
- `DeltaF_phys_cert_normalized`: `0.00174292636665839`
- `finite_correction_half_cert`: `0.000871463183329195`
- `alpha_inv_pred_blind_v13`: `257.1950111578061`
- `correction_to_leading_ratio`: `3.3883477452632444e-06`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_CERTIFIED_LENGTH_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing candidate only shows that the certified-length branch and finite-correction normalizer are internally alpha-blind and subleading.
The next gate is a BEMv14 convergence grid for the certified-length budget, reusing the BEMv10 stability logic.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v18_knotplot\runs\7_1\bemv8_base`

## Files

- `certified_length_audit.csv`
- `certified_normalizer_candidates.csv`
- `alpha_component_budget_v13.csv`