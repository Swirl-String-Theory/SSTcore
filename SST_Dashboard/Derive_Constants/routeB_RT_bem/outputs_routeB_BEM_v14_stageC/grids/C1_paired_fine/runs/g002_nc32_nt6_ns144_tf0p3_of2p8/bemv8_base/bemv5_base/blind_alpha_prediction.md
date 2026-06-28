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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C1_paired_fine\runs\g002_nc32_nt6_ns144_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `252`
- `M_min`: `84`
- `M_max`: `335`
- `rms`: `0.00046579013112357684`
- `S_ren`: `-79.39885243772211`
- `S_ren_se`: `12.395375554757187`
- `alpha_inv_half_RT_only`: `-39.699426218861056`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-62.643691618576554`
- `alpha_inv_pred_blind_with_soft`: `-31.321845809288277`
- `a_M`: `0.011170947171421808`
- `a_M_se`: `0.0022847517308375903`
- `a_sqrtM`: `-1.380479779856628`
- `a_sqrtM_se`: `0.24376374308064916`
- `a_logM`: `15.006282240088042`
- `a_logM_se`: `2.4090740184643877`
- `b_inv_sqrt`: `275.89985655481195`
- `b_inv_sqrt_se`: `41.813178170443855`
- `b_inv`: `-458.02459418945335`
- `b_inv_se`: `67.20879611921708`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `252`
- `M_min`: `84`
- `M_max`: `335`
- `rms`: `0.0010524888541231024`
- `S_inf`: `-0.3099208329448313`
- `S_inf_se`: `0.011007773905135089`
- `alpha_inv_pred_blind`: `-0.15496041647241565`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=335, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=335, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=335, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.