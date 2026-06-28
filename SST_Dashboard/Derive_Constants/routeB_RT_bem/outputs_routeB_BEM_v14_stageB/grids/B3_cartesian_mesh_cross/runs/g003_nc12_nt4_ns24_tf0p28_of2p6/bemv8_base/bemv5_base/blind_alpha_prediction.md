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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g003_nc12_nt4_ns24_tf0p28_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0052319790864413475`
- `S_ren`: `1426.296934348516`
- `S_ren_se`: `211.7789070575052`
- `alpha_inv_half_RT_only`: `713.148467174258`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `1443.0520951676617`
- `alpha_inv_pred_blind_with_soft`: `721.5260475838309`
- `a_M`: `-2.1711333785421516`
- `a_M_se`: `0.2637178626402711`
- `a_sqrtM`: `98.49526263131776`
- `a_sqrtM_se`: `12.954596117788403`
- `a_logM`: `-414.6559360207529`
- `a_logM_se`: `58.93292685680567`
- `b_inv_sqrt`: `-3071.0674151197127`
- `b_inv_sqrt_se`: `470.72579766737493`
- `b_inv`: `2111.134911140159`
- `b_inv_se`: `348.1113181612894`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.017831660599627718`
- `S_inf`: `-3.523638625906978`
- `S_inf_se`: `0.4036839823576362`
- `alpha_inv_pred_blind`: `-1.761819312953489`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.