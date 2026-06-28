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

- input path: `/mnt/data/outputs_routeB_BEM_v6_fast/runs/g001_nc8_nt3_ns14_tf0p38_of2p2/idealxml_sampled_ideal_used.txt`
- input sha256: `f05c65f845f5e00742e92da382adbfe5b1095401368ce8776282a1966a5a2a21`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
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
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0019169920827338224`
- `S_ren`: `-267.4319664131332`
- `S_ren_se`: `112.77297277544707`
- `alpha_inv_half_RT_only`: `-133.7159832065666`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-250.6768055939876`
- `alpha_inv_pred_blind_with_soft`: `-125.3384027969938`
- `a_M`: `0.8020370853676262`
- `a_M_se`: `0.3180110002525101`
- `a_sqrtM`: `-28.107115766145455`
- `a_sqrtM_se`: `11.41717524575267`
- `a_logM`: `91.3601609327149`
- `a_logM_se`: `37.98717050195918`
- `b_inv_sqrt`: `525.362171232882`
- `b_inv_sqrt_se`: `222.07883437941516`
- `b_inv`: `-281.9858419079272`
- `b_inv_se`: `120.29034865269573`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0023272050922955624`
- `S_inf`: `-0.29015733112678616`
- `S_inf_se`: `0.08311490113443866`
- `alpha_inv_pred_blind`: `-0.14507866556339308`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=37, Id=0:1:1, L=6.283185307179586
- `3_1`: `raw_spectrum_3_1.npy`, modes=37, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=37, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.