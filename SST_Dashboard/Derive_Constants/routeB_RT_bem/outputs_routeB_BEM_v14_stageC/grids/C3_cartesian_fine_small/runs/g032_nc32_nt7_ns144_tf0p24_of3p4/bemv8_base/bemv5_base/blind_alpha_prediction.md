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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g032_nc32_nt7_ns144_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `276`
- `M_min`: `92`
- `M_max`: `367`
- `rms`: `0.0005437006559206466`
- `S_ren`: `83.996689151949`
- `S_ren_se`: `14.074092742730851`
- `alpha_inv_half_RT_only`: `41.9983445759745`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `100.75184997109456`
- `alpha_inv_pred_blind_with_soft`: `50.37592498554728`
- `a_M`: `-0.015080246927898278`
- `a_M_se`: `0.0023266537278099457`
- `a_sqrtM`: `1.596486854005712`
- `a_sqrtM_se`: `0.2598225229367072`
- `a_logM`: `-16.106362121393524`
- `a_logM_se`: `2.687666599274586`
- `b_inv_sqrt`: `-292.63278814590564`
- `b_inv_sqrt_se`: `48.8268493450306`
- `b_inv`: `500.92552122308325`
- `b_inv_se`: `82.1475593066349`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `276`
- `M_min`: `92`
- `M_max`: `367`
- `rms`: `0.0008255776843120951`
- `S_inf`: `-0.37497593373774624`
- `S_inf_se`: `0.00825116450519867`
- `alpha_inv_pred_blind`: `-0.18748796686887312`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=367, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=367, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=367, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.