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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D1_ultra_paired_48_64_80\runs\g003_nc80_nt12_ns512_tf0p16_of4p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `1104`
- `M_min`: `368`
- `M_max`: `1471`
- `rms`: `0.0005132425775311304`
- `S_ren`: `454.5847505915452`
- `S_ren_se`: `8.420428125159619`
- `alpha_inv_half_RT_only`: `227.2923752957726`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `471.3399114106907`
- `alpha_inv_pred_blind_with_soft`: `235.66995570534536`
- `a_M`: `-0.015299777542790272`
- `a_M_se`: `0.00027443897056382576`
- `a_sqrtM`: `3.3644306582832275`
- `a_sqrtM_se`: `0.06136282179632042`
- `a_logM`: `-68.82940861606443`
- `a_logM_se`: `1.270984238798788`
- `b_inv_sqrt`: `-2480.882448469585`
- `b_inv_sqrt_se`: `46.23620294264749`
- `b_inv`: `8290.46104682919`
- `b_inv_se`: `155.77564934552822`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `1104`
- `M_min`: `368`
- `M_max`: `1471`
- `rms`: `0.001155165846840498`
- `S_inf`: `-0.2718499102492057`
- `S_inf_se`: `0.005776750006578911`
- `alpha_inv_pred_blind`: `-0.13592495512460284`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1471, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1471, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1471, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.