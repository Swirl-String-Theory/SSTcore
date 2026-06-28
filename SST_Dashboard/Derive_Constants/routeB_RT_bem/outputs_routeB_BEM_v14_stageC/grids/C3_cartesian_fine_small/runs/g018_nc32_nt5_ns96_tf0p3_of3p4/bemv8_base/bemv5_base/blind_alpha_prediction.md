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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g018_nc32_nt5_ns96_tf0p3_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `192`
- `M_min`: `64`
- `M_max`: `255`
- `rms`: `0.0006347819002945447`
- `S_ren`: `9.889007284125775`
- `S_ren_se`: `18.320307027870044`
- `alpha_inv_half_RT_only`: `4.944503642062887`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `26.644168103271337`
- `alpha_inv_pred_blind_with_soft`: `13.322084051635668`
- `a_M`: `-0.0012699725499266054`
- `a_M_se`: `0.004685173555760987`
- `a_sqrtM`: `0.13711317016314864`
- `a_sqrtM_se`: `0.436104655497176`
- `a_logM`: `-1.7241445477226838`
- `a_logM_se`: `3.7600787412809664`
- `b_inv_sqrt`: `-39.502753318977945`
- `b_inv_sqrt_se`: `56.93443871509038`
- `b_inv`: `79.13130434292533`
- `b_inv_se`: `79.83489367093397`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `192`
- `M_min`: `64`
- `M_max`: `255`
- `rms`: `0.0006514717428524185`
- `S_inf`: `-0.22824497797003096`
- `S_inf_se`: `0.007804403849684837`
- `alpha_inv_pred_blind`: `-0.11412248898501548`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=255, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=255, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=255, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.