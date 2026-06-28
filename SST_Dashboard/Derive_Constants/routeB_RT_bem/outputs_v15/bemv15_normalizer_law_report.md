# BEMv15 normalizer law report

This report is alpha-blind: it does not contain or compare against observed fine structure.

## Core claim

BEMv15 promotes the repeatedly selected BEMv14 normalizer to a conditional normalizer law:

\[
\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}
\]

The claim is conditional: it follows from mode-extensivity plus length-scale covariance. It is not yet a full heat-kernel theorem.

## Global numerical certificate

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

## Stage consensus

- `StageC`: `M_Lcert2` selected by `5` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `1.2241728079540825e-05`
- `StageA`: `M_Lcert2` selected by `3` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `0.0028263191049214646`
- `StageB`: `M_Lcert2` selected by `5` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `0.0003698544154412709`
- `StageD`: `M_Lcert2` selected by `3` grid families; gate `PASS_CROSS_GRID_CONSENSUS`; aggregate CV `5.894392513597223e-06`

## Interpretation

The supplied Stage A/B/C/D data give strong numerical support for \(M_{\max}L_{
m cert}^{2}\) as the Route-B certified-length normalizer.

The remaining theoretical task is no longer another blind numerical search. It is an analytic derivation of mode extensivity and the \(L_{
m cert}^{2}\) scale-covariance factor from the R--T boundary operator.

## Next gate

\[
\boxed{\text{BEMv16: heat-kernel / DtN proof of } \mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}
\]

## Asymptotic subset note

The global A/B/C/D mean includes deliberately coarse probe grids. For the asymptotic numerical value, use the Stage C+D or Stage D subset certificate. The normalizer-selection evidence uses all stages; the value-estimate should be read from the finer subsets.
