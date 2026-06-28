# BEMv16 heat-kernel / DtN normalizer report

This report is alpha-blind. It does not contain or compare against observed fine structure.

## Result

BEMv16 converts the BEMv15 normalizer law into a heat-kernel/DtN proof-obligation certificate:

\[
\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}
\]

The result is conditional on mode-extensivity and second-order length-scale covariance.

## Numerical link from BEMv15

- `preferred_normalizer`: `M_Lcert2`
- `stages_detected`: `StageA,StageB,StageC,StageD`
- `n_stages`: `4`
- `n_grid_families`: `16`
- `preferred_selected_count`: `16`
- `preferred_selected_fraction`: `1.0`
- `pass_grid_family_count`: `16`
- `pass_grid_family_fraction`: `1.0`
- `preferred_cross_grid_consensus_pass_count`: `4`
- `global_alpha_inv_blind_mean`: `137.22356337162375`
- `global_alpha_inv_blind_std`: `0.22297776507024064`
- `global_alpha_inv_blind_span`: `1.294308030038792`
- `global_alpha_inv_blind_cv_abs`: `0.001624923297366798`
- `global_abs_correction_ratio_max`: `0.00930461683469654`
- `global_numeric_gate`: `PASS_G14_NUMERIC_SUPPORT_FOR_M_LCERT2`
- `analytic_status`: `CONDITIONAL_LAW_UNDER_H1_MODE_EXTENSIVITY_AND_H2_SCALE_COVARIANCE`
- `stageD_alpha_inv_mean`: `137.15486676613227`
- `stageD_alpha_inv_cv_abs`: `5.894392513597222e-06`
- `stageCD_alpha_inv_mean`: `137.15528451885825`
- `stageCD_alpha_inv_cv_abs`: `1.1352779235901546e-05`
- `canonical_scan_a_M_exponent`: `1.0`
- `canonical_scan_b_L_exponent`: `2.0`
- `canonical_scan_normalizer_formula`: `M^1 L^2`
- `canonical_scan_n_points`: `145`
- `canonical_scan_alpha_inv_mean`: `137.22356337162375`
- `canonical_scan_alpha_inv_std`: `0.22297776507024064`
- `canonical_scan_alpha_inv_span`: `1.294308030038792`
- `canonical_scan_alpha_inv_cv_abs`: `0.001624923297366798`
- `canonical_scan_abs_correction_ratio_max`: `0.00930461683469654`
- `canonical_scan_numeric_gate`: `PASS_NUMERIC_STABILITY`
- `canonical_scan_note`: `CANONICAL_CANDIDATE_M_LCERT2`

## Interpretation

The numerical search phase is now largely exhausted. The remaining issue is mathematical: derive the length-squared covariance from the R--T boundary operator's principal symbol and heat-kernel coefficients.

## BEMv17 target

\[
\boxed{\text{BEMv17: principal-symbol and heat-kernel coefficient derivation for }L_{\rm cert}^{2}.}
\]