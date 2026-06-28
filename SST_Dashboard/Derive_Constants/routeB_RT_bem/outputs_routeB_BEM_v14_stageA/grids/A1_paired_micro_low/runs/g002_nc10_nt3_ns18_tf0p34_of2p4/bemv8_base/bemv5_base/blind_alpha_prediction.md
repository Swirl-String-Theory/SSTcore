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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A1_paired_micro_low\runs\g002_nc10_nt3_ns18_tf0p34_of2p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.001763455520201894`
- `S_ren`: `-247.3113337377565`
- `S_ren_se`: `79.0301387377927`
- `alpha_inv_half_RT_only`: `-123.65566686887826`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-230.55617291861094`
- `alpha_inv_pred_blind_with_soft`: `-115.27808645930547`
- `a_M`: `0.5413570893231103`
- `a_M_se`: `0.16771133291300708`
- `a_sqrtM`: `-21.375215612599376`
- `a_sqrtM_se`: `6.707024130498973`
- `a_logM`: `78.20810666356367`
- `a_logM_se`: `24.836874394037373`
- `b_inv_sqrt`: `505.18660443897903`
- `b_inv_sqrt_se`: `161.4676032119864`
- `b_inv`: `-303.7478316094015`
- `b_inv_se`: `97.17521523918211`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.002091470599118213`
- `S_inf`: `-0.2189756919332696`
- `S_inf_se`: `0.05835979852794047`
- `alpha_inv_pred_blind`: `-0.1094878459666348`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.