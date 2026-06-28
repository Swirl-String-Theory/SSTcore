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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B2_paired_medium\runs\g002_nc20_nt5_ns48_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `111`
- `M_min`: `37`
- `M_max`: `147`
- `rms`: `0.0009657699880950648`
- `S_ren`: `-32.46965906582636`
- `S_ren_se`: `32.50896790914646`
- `alpha_inv_half_RT_only`: `-16.23482953291318`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-15.714498246680801`
- `alpha_inv_pred_blind_with_soft`: `-7.8572491233404005`
- `a_M`: `0.0022844705929255804`
- `a_M_se`: `0.01626345884298`
- `a_sqrtM`: `-0.6005279079737728`
- `a_sqrtM_se`: `1.1493338635427575`
- `a_logM`: `6.42433135486598`
- `a_logM_se`: `7.523022176105169`
- `b_inv_sqrt`: `99.63318896352068`
- `b_inv_sqrt_se`: `86.47307207986242`
- `b_inv`: `-130.5677246908246`
- `b_inv_se`: `92.04047607304625`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `111`
- `M_min`: `37`
- `M_max`: `147`
- `rms`: `0.0015759151252933172`
- `S_inf`: `-0.3820488071388798`
- `S_inf_se`: `0.024824613908465874`
- `alpha_inv_pred_blind`: `-0.1910244035694399`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=147, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=147, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=147, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.