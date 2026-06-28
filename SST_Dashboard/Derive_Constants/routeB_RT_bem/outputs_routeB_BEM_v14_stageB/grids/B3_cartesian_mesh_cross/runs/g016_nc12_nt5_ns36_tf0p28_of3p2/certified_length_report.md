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

- `target`: `3_1`
- `reference`: `0_1`
- `normalizer`: `M_Lcert2`
- `L_cert_target`: `16.371637`
- `NsoftV`: `16.755160819145562`
- `leading_full_cert`: `274.30941080767377`
- `leading_half_alpha_inv_cert`: `137.15470540383689`
- `DeltaF_pair_raw`: `7180.733935196241`
- `normalizer_denominator`: `25462.897315678056`
- `DeltaF_phys_cert_normalized`: `0.2820077325126276`
- `finite_correction_half_cert`: `0.1410038662563138`
- `alpha_inv_pred_blind_v13`: `137.2957092700932`
- `correction_to_leading_ratio`: `0.001028064373301255`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_CERTIFIED_LENGTH_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing candidate only shows that the certified-length branch and finite-correction normalizer are internally alpha-blind and subleading.
The next gate is a BEMv14 convergence grid for the certified-length budget, reusing the BEMv10 stability logic.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g016_nc12_nt5_ns36_tf0p28_of3p2\bemv8_base`

## Files

- `certified_length_audit.csv`
- `certified_normalizer_candidates.csv`
- `alpha_component_budget_v13.csv`