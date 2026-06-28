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

- input path: `outputs_routeB_BEM_v18_knotplot\runs\7_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `7412e53ebafaec7970f0f977690187bf1ff3ecd4ee9c2605dd3d0636be81ae16`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `7_1`
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
- `rms`: `0.002301542847953115`
- `S_ren`: `353.1851438112578`
- `S_ren_se`: `69.76837755516664`
- `alpha_inv_half_RT_only`: `176.5925719056289`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `369.9403046304033`
- `alpha_inv_pred_blind_with_soft`: `184.97015231520166`
- `a_M`: `-0.14908611994587018`
- `a_M_se`: `0.02193129106438989`
- `a_sqrtM`: `11.249359499659002`
- `a_sqrtM_se`: `1.874435498350323`
- `a_logM`: `-79.05813133400231`
- `a_logM_se`: `14.83920327381479`
- `b_inv_sqrt`: `-979.7893864768606`
- `b_inv_sqrt_se`: `206.30743401836995`
- `b_inv`: `1129.011067225549`
- `b_inv_se`: `265.6139862835919`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.005852780610159721`
- `S_inf`: `-1.6928685928229272`
- `S_inf_se`: `0.07632237010637428`
- `alpha_inv_pred_blind`: `-0.8464342964114636`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `7_1`: `raw_spectrum_7_1.npy`, modes=215, Id=7:1:1, L=30.700289

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.