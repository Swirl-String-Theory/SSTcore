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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g018_nc10_nt3_ns14_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.0013871212430343251`
- `S_ren`: `-272.53021925233486`
- `S_ren_se`: `63.61693558315446`
- `alpha_inv_half_RT_only`: `-136.26510962616743`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-255.7750584331893`
- `alpha_inv_pred_blind_with_soft`: `-127.88752921659464`
- `a_M`: `0.6645696793189053`
- `a_M_se`: `0.15171572568660455`
- `a_sqrtM`: `-25.212006809953333`
- `a_sqrtM_se`: `5.804799556952883`
- `a_logM`: `88.55466101221403`
- `a_logM_se`: `20.5651446990255`
- `b_inv_sqrt`: `547.1699200112125`
- `b_inv_sqrt_se`: `127.90416198472548`
- `b_inv`: `-313.292870521566`
- `b_inv_se`: `73.63849031480706`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.0018378079074626394`
- `S_inf`: `-0.11989696077346507`
- `S_inf_se`: `0.05369321402287638`
- `alpha_inv_pred_blind`: `-0.05994848038673253`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=43, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=43, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=43, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.