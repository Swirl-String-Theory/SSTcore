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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D1_ultra_paired_48_64_80\runs\g002_nc64_nt10_ns384_tf0p2_of3p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0006746338549154712`
- `S_ren`: `29.268724842345677`
- `S_ren_se`: `12.538095356265377`
- `alpha_inv_half_RT_only`: `14.634362421172838`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `46.023885661491235`
- `alpha_inv_pred_blind_with_soft`: `23.011942830745618`
- `a_M`: `-0.00019041735745704141`
- `a_M_se`: `0.0006217074202729172`
- `a_sqrtM`: `0.12010852393779033`
- `a_sqrtM_se`: `0.11592312778923519`
- `a_logM`: `-3.985273286099814`
- `a_logM_se`: `2.0022866101889263`
- `b_inv_sqrt`: `-190.2471311323775`
- `b_inv_sqrt_se`: `60.74160520273005`
- `b_inv`: `744.1365871952104`
- `b_inv_se`: `170.6547477815768`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0007350324075914237`
- `S_inf`: `-0.24778064427484636`
- `S_inf_se`: `0.004406517101274216`
- `alpha_inv_pred_blind`: `-0.12389032213742318`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.