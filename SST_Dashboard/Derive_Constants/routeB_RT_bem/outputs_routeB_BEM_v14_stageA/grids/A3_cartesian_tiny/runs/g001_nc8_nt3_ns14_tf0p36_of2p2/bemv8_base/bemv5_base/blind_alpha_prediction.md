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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g001_nc8_nt3_ns14_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.002010100924155686`
- `S_ren`: `-271.21517578220494`
- `S_ren_se`: `118.24965627552845`
- `alpha_inv_half_RT_only`: `-135.60758789110247`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-254.46001496305936`
- `alpha_inv_pred_blind_with_soft`: `-127.23000748152968`
- `a_M`: `0.799275567185024`
- `a_M_se`: `0.33345483512612817`
- `a_sqrtM`: `-28.19744475162709`
- `a_sqrtM_se`: `11.971636779695698`
- `a_logM`: `92.25022461232358`
- `a_logM_se`: `39.8319717072252`
- `b_inv_sqrt`: `533.7861035109684`
- `b_inv_sqrt_se`: `232.86382567618352`
- `b_inv`: `-288.15236218147226`
- `b_inv_se`: `126.13210642237274`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0023348435442995226`
- `S_inf`: `-0.3251458120738269`
- `S_inf_se`: `0.08338770441728713`
- `alpha_inv_pred_blind`: `-0.16257290603691346`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=37, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=37, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=37, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.