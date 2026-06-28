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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g021_nc16_nt4_ns36_tf0p32_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `75`
- `M_min`: `25`
- `M_max`: `99`
- `rms`: `0.0009174476359332835`
- `S_ren`: `404.39545622483035`
- `S_ren_se`: `34.20999102609029`
- `alpha_inv_half_RT_only`: `202.19772811241518`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `421.1506170439759`
- `alpha_inv_pred_blind_with_soft`: `210.57530852198795`
- `a_M`: `-0.34583876834766336`
- `a_M_se`: `0.027972085115249873`
- `a_sqrtM`: `19.689519960618085`
- `a_sqrtM_se`: `1.6222958731694195`
- `a_logM`: `-103.94765907439562`
- `a_logM_se`: `8.714010803835727`
- `b_inv_sqrt`: `-963.1860699215306`
- `b_inv_sqrt_se`: `82.18962683395812`
- `b_inv`: `826.0728605207582`
- `b_inv_se`: `71.77823261675313`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `75`
- `M_min`: `25`
- `M_max`: `99`
- `rms`: `0.001840917270844789`
- `S_inf`: `-0.3777858873954764`
- `S_inf_se`: `0.03529902918686646`
- `alpha_inv_pred_blind`: `-0.1888929436977382`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=99, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=99, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=99, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.