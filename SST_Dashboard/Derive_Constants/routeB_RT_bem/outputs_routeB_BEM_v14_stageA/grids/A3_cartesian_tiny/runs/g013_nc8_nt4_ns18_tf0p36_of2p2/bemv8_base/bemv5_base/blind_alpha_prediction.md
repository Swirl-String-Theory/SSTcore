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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g013_nc8_nt4_ns18_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `37`
- `M_min`: `13`
- `M_max`: `49`
- `rms`: `0.0659477362837424`
- `S_ren`: `32652.80738481831`
- `S_ren_se`: `3419.9149912769217`
- `alpha_inv_half_RT_only`: `16326.403692409154`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `32669.562545637455`
- `alpha_inv_pred_blind_with_soft`: `16334.781272818727`
- `a_M`: `-75.07801791526026`
- `a_M_se`: `6.715488873765202`
- `a_sqrtM`: `2906.428860813382`
- `a_sqrtM_se`: `276.48703412992705`
- `a_logM`: `-10448.500710065857`
- `a_logM_se`: `1054.8147597756706`
- `b_inv_sqrt`: `-66140.20121657707`
- `b_inv_sqrt_se`: `7069.901528984932`
- `b_inv`: `38872.81016886778`
- `b_inv_se`: `4389.8605447126065`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `37`
- `M_min`: `13`
- `M_max`: `49`
- `rms`: `0.30790105211196495`
- `S_inf`: `-58.62449480601115`
- `S_inf_se`: `9.222958380801504`
- `alpha_inv_pred_blind`: `-29.312247403005575`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=49, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=49, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=49, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.