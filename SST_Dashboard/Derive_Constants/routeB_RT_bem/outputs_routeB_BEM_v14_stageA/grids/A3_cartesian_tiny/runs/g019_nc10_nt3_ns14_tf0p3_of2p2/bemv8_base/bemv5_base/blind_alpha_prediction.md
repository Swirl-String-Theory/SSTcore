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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g019_nc10_nt3_ns14_tf0p3_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `fcceea85baf053a7371e73c1e34e425df7930b2f9f7d82c56b811758fda86dee`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `3_1`
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
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.002191877665278586`
- `S_ren`: `-418.0472293253516`
- `S_ren_se`: `100.52512780581235`
- `alpha_inv_half_RT_only`: `-209.0236146626758`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-401.2920685062061`
- `alpha_inv_pred_blind_with_soft`: `-200.64603425310304`
- `a_M`: `1.0264830513278778`
- `a_M_se`: `0.23973557630518696`
- `a_sqrtM`: `-38.897547823158746`
- `a_sqrtM_se`: `9.172529484496698`
- `a_logM`: `136.19377269787915`
- `a_logM_se`: `32.4962807507814`
- `b_inv_sqrt`: `837.6345750820188`
- `b_inv_sqrt_se`: `202.10942436237838`
- `b_inv`: `-476.9834061735028`
- `b_inv_se`: `116.36081779901411`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.0028756308003548567`
- `S_inf`: `-0.4092986304489873`
- `S_inf_se`: `0.08401414499701594`
- `alpha_inv_pred_blind`: `-0.20464931522449364`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=43, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=43, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=43, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.