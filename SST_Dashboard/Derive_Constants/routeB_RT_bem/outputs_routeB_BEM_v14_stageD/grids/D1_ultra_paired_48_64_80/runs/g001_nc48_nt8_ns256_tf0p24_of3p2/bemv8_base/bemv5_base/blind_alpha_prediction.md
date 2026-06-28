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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D1_ultra_paired_48_64_80\runs\g001_nc48_nt8_ns256_tf0p24_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0004979890656498325`
- `S_ren`: `-165.15578990494052`
- `S_ren_se`: `10.820055188384988`
- `alpha_inv_half_RT_only`: `-82.57789495247026`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-148.40062908579495`
- `alpha_inv_pred_blind_with_soft`: `-74.20031454289747`
- `a_M`: `0.014975111916355976`
- `a_M_se`: `0.0009288064238671484`
- `a_sqrtM`: `-2.187730421758312`
- `a_sqrtM_se`: `0.13687025871216324`
- `a_logM`: `28.957201411801297`
- `a_logM_se`: `1.868352459434267`
- `b_inv_sqrt`: `657.815661528604`
- `b_inv_sqrt_se`: `44.792564766120584`
- `b_inv`: `-1357.4680200396788`
- `b_inv_se`: `99.45316106331092`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0006908712025266638`
- `S_inf`: `-0.3381216700421363`
- `S_inf_se`: `0.005237787867886816`
- `alpha_inv_pred_blind`: `-0.16906083502106814`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=639, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=639, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=639, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.