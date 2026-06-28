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

- `target`: `4_1`
- `reference`: `0_1`
- `normalizer`: `M_Lcert2`
- `L_cert_target`: `21.043322`
- `NsoftV`: `16.755160819145562`
- `leading_full_cert`: `352.58424427906385`
- `leading_half_alpha_inv_cert`: `176.29212213953193`
- `DeltaF_pair_raw`: `-91.87101379079677`
- `normalizer_denominator`: `95206.60117107206`
- `DeltaF_phys_cert_normalized`: `-0.0009649647467796719`
- `finite_correction_half_cert`: `-0.00048248237338983593`
- `alpha_inv_pred_blind_v13`: `176.29163965715853`
- `correction_to_leading_ratio`: `2.73683456489315e-06`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_CERTIFIED_LENGTH_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing candidate only shows that the certified-length branch and finite-correction normalizer are internally alpha-blind and subleading.
The next gate is a BEMv14 convergence grid for the certified-length budget, reusing the BEMv10 stability logic.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v18_knotplot\runs\4_1\bemv8_base`

## Files

- `certified_length_audit.csv`
- `certified_normalizer_candidates.csv`
- `alpha_component_budget_v13.csv`