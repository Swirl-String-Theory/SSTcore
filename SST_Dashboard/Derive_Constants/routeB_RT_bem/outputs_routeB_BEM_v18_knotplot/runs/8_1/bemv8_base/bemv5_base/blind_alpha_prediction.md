# Blind Route-B BEMv5 alpha-prediction audit

## Status

This report is alpha-blind: it does not contain or compare against CODATA alpha.

BEMv5 separates the candidate action into

\[
S_{\rm total}=S_{\rm soft}+S_{\rm RT}^{\rm ren}.
\]

The provisional Route-B working map is

\[
\alpha_{\rm inv,pred}^{\rm blind}=\frac12 S_{\rm total}.
\]

This map is not yet a theorem.

## Provenance

- input path: `outputs_routeB_BEM_v18_knotplot\runs\8_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `6076fa5aca2fec22d8bf0d9c34a4741f183a5b28721fb85fbbf2c95335381311`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `8_1`
- reference/vacuum subtraction: `0_1`
- backend: `BEM_V5_SOFT_INDEX_HEAT_KERNEL`
- scipy generalized eigensolver: `True`

## Soft-sector term

- `soft_index_count`: `4`
- `soft_volume_mode`: `unit_ball`
- `soft_volume_value`: `4.1887902047863905`
- `soft_action`: `16.755160819145562`
- `soft_alpha_inv_half`: `8.377580409572781`
- `status`: `EXPLICIT_SEPARATED_SOFT_TERM_NOT_ALPHA_FIT`

## Selected heat-kernel counterterm fit

- `counterterm_model`: `hk+inv_sqrt+inv`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.01590164826617437`
- `S_ren`: `10023.876453072888`
- `S_ren_se`: `482.0384730054415`
- `alpha_inv_half_RT_only`: `5011.938226536444`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `10040.631613892034`
- `alpha_inv_pred_blind_with_soft`: `5020.315806946017`
- `a_M`: `-3.754966289181766`
- `a_M_se`: `0.15152604125496835`
- `a_sqrtM`: `297.96939413118565`
- `a_sqrtM_se`: `12.950710006944572`
- `a_logM`: `-2196.899854986839`
- `a_logM_se`: `102.52591700403268`
- `b_inv_sqrt`: `-28551.59367502045`
- `b_inv_sqrt_se`: `1425.4039430005548`
- `b_inv`: `34481.99140935852`
- `b_inv_se`: `1835.160352636713`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.08422807927178018`
- `S_inf`: `-16.489485292426675`
- `S_inf_se`: `1.098364532641248`
- `alpha_inv_pred_blind`: `-8.244742646213338`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `8_1`: `raw_spectrum_8_1.npy`, modes=215, Id=8:1:1, L=35.491375

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.