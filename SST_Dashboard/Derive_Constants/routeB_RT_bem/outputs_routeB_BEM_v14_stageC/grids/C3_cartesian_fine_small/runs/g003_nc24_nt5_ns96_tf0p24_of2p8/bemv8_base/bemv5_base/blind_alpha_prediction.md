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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g003_nc24_nt5_ns96_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0008593736505300353`
- `S_ren`: `8.988540457671647`
- `S_ren_se`: `26.050831669053817`
- `alpha_inv_half_RT_only`: `4.494270228835823`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `25.74370127681721`
- `alpha_inv_pred_blind_with_soft`: `12.871850638408604`
- `a_M`: `-0.005923056528326517`
- `a_M_se`: `0.008188930168996541`
- `a_sqrtM`: `0.3451189922555985`
- `a_sqrtM_se`: `0.6998959321278809`
- `a_logM`: `-2.0765624554240056`
- `a_logM_se`: `5.54081376313149`
- `b_inv_sqrt`: `-26.57015030971295`
- `b_inv_sqrt_se`: `77.03318357141559`
- `b_inv`: `38.18314945871237`
- `b_inv_se`: `99.17767172024209`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0011693714264601573`
- `S_inf`: `-0.5119989353833575`
- `S_inf_se`: `0.015249025163729038`
- `alpha_inv_pred_blind`: `-0.25599946769167875`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.