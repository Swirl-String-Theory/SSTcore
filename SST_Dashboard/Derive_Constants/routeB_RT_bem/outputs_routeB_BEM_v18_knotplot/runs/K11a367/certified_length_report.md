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

- `target`: `K11a367`
- `reference`: `0_1`
- `normalizer`: `M_Lcert2`
- `L_cert_target`: `44.804989`
- `NsoftV`: `16.755160819145562`
- `leading_full_cert`: `750.7147961950479`
- `leading_half_alpha_inv_cert`: `375.35739809752397`
- `DeltaF_pair_raw`: `7717.494251498315`
- `normalizer_denominator`: `431609.71344737604`
- `DeltaF_phys_cert_normalized`: `0.01788072420765681`
- `finite_correction_half_cert`: `0.008940362103828405`
- `alpha_inv_pred_blind_v13`: `375.3663384596278`
- `correction_to_leading_ratio`: `2.3818265336295712e-05`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_CERTIFIED_LENGTH_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing candidate only shows that the certified-length branch and finite-correction normalizer are internally alpha-blind and subleading.
The next gate is a BEMv14 convergence grid for the certified-length budget, reusing the BEMv10 stability logic.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v18_knotplot\runs\K11a367\bemv8_base`

## Files

- `certified_length_audit.csv`
- `certified_normalizer_candidates.csv`
- `alpha_component_budget_v13.csv`