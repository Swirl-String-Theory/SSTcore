# Blind BEMv7 spectral-length alpha budget

This report is alpha-blind: it does not contain or compare against CODATA alpha.

BEMv7 uses the working Route-B split

\[
\alpha^{-1}_{\rm pred,blind}=\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm HK}(3_1)+\Delta_{\rm RT}^{\rm ren}(3_1/0_1)\right].
\]

This is a falsifiable component budget, not yet a theorem.

## Spectral length

\[L_{\rm HK}(K)=2\pi\,A_{\rm lead}(K)/A_{\rm lead}(0_1).\]

- length coefficient: `A_M`
- length fit model: `hk+inv_sqrt+inv`

## Component budget

- `target`: `3_1`
- `reference`: `0_1`
- `soft_index_count`: `4`
- `soft_volume_mode`: `unit_ball`
- `soft_volume`: `4.1887902047863905`
- `S_soft_per_unit_length`: `16.755160819145562`
- `length_coeff`: `A_M`
- `L_HK_target`: `3.1830679242521107`
- `leading_length_term_half_NsoftVsoftL`: `26.66640748455398`
- `Delta_RT_ren_target_reference`: `-428.43705303812476`
- `finite_correction_half`: `-214.21852651906238`
- `alpha_inv_pred_blind_v7`: `-187.5521190345084`
- `status`: `ALPHA_BLIND_COMPONENT_BUDGET_NOT_CODATA_COMPARISON`

## Outputs

- `hk_length_coefficients.csv`
- `spectral_length_estimate.csv`
- `finite_rt_correction.csv`
- `alpha_component_budget.csv`
- `bemv5_base/` or reused BEMv5 folder with raw spectra

## Interpretation

The next gate is convergence: `L_HK`, `Delta_RT^ren`, and the total blind budget must stabilize under mesh, tube-radius, and outer-boundary refinement.

Input/source: `BEMv5 subrun=outputs_routeB_BEM_v7\bemv5_base`