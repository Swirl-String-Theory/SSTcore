# Blind BEMv8 pair-subtracted length budget

## Status

This report is alpha-blind. It does not contain or compare against observed alpha.

BEMv8 uses

\[
\alpha^{-1}_{\rm pred,blind}
=\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm long}(3_1)
+\Delta F_{\rm pair}(3_1/0_1)\right].
\]

The large term uses restored longitudinal scale; the finite term uses direct pair subtraction.

## Component budget

- `target`: `9_1`
- `reference`: `0_1`
- `soft_index_count`: `4`
- `soft_volume_mode`: `unit_ball`
- `soft_volume`: `4.1887902047863905`
- `S_soft_per_unit_length`: `16.755160819145562`
- `length_source`: `geometric_raw`
- `length_coeff`: `A_M`
- `L_long_target`: `37.7543179229535`
- `leading_length_term_half_NsoftVsoftL`: `316.2898342081177`
- `DeltaF_pair_target_reference`: `9589.564498380354`
- `finite_correction_half_pair`: `4794.782249190177`
- `alpha_inv_pred_blind_v8`: `5111.072083398295`
- `status`: `ALPHA_BLIND_BEMV8_PAIR_LENGTH_BUDGET_NOT_CODATA_COMPARISON`

## Output files

- `geometric_length_audit.csv`
- `hk_length_coefficients_phys.csv`
- `spectral_length_estimate_phys.csv`
- `pair_subtracted_correction.csv`
- `alpha_component_budget_v8.csv`
- `bemv5_base/` or reused BEMv5 folder

## Interpretation

BEMv8 fixes the two main BEMv7 pathologies: unit-length suppression of the longitudinal scale and independent subtraction of two unstable constants.
It is still a falsifier. The next gate is convergence of `L_long`, `DeltaF_pair`, and the blind budget under mesh/tube/outer-boundary refinement.

Input/source: `BEMv5 subrun=outputs_routeB_BEM_v18_knotplot\runs\9_1\bemv8_base\bemv5_base`