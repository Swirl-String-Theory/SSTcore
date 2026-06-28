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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g005_nc12_nt4_ns36_tf0p32_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `63`
- `M_min`: `21`
- `M_max`: `83`
- `rms`: `0.0025458343158821376`
- `S_ren`: `690.4668945536382`
- `S_ren_se`: `99.18245839045055`
- `alpha_inv_half_RT_only`: `345.2334472768191`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `707.2220553727838`
- `alpha_inv_pred_blind_with_soft`: `353.6110276863919`
- `a_M`: `-0.7668104975710346`
- `a_M_se`: `0.1012690642828763`
- `a_sqrtM`: `39.28148091938276`
- `a_sqrtM_se`: `5.378106682799198`
- `a_logM`: `-187.17945405616018`
- `a_logM_se`: `26.451375205335506`
- `b_inv_sqrt`: `-1570.7434396645485`
- `b_inv_sqrt_se`: `228.43384288861583`
- `b_inv`: `1223.7362031894172`
- `b_inv_se`: `182.65483716800497`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `63`
- `M_min`: `21`
- `M_max`: `83`
- `rms`: `0.004833074112684456`
- `S_inf`: `-1.2293497792864228`
- `S_inf_se`: `0.10118837624437875`
- `alpha_inv_pred_blind`: `-0.6146748896432114`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=83, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=83, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=83, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.