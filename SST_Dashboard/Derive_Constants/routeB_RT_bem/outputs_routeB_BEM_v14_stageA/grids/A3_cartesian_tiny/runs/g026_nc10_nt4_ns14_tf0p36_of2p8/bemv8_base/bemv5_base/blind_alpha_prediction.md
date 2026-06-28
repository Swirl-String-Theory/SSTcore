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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g026_nc10_nt4_ns14_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `40`
- `M_min`: `14`
- `M_max`: `53`
- `rms`: `0.0017550595741865557`
- `S_ren`: `539.2998625835224`
- `S_ren_se`: `88.18575696655002`
- `alpha_inv_half_RT_only`: `269.6499312917612`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `556.055023402668`
- `alpha_inv_pred_blind_with_soft`: `278.027511701334`
- `a_M`: `-1.0877111786460052`
- `a_M_se`: `0.1566359352533577`
- `a_sqrtM`: `44.17397608251529`
- `a_sqrtM_se`: `6.701830051373294`
- `a_logM`: `-167.05926787261384`
- `a_logM_se`: `26.569754080452785`
- `b_inv_sqrt`: `-1114.8619048731368`
- `b_inv_sqrt_se`: `185.05697153503493`
- `b_inv`: `692.9187985795397`
- `b_inv_se`: `119.40216527537278`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `40`
- `M_min`: `14`
- `M_max`: `53`
- `rms`: `0.00469646720428368`
- `S_inf`: `-1.3075816875617754`
- `S_inf_se`: `0.13421823406565442`
- `alpha_inv_pred_blind`: `-0.6537908437808877`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=53, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=53, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=53, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.