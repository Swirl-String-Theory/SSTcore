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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C5_sphere_boundary_only\runs\g003_nc40_nt7_ns196_tf0p2_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `147`
- `M_min`: `49`
- `M_max`: `195`
- `rms`: `2.4051370800635005e-15`
- `S_ren`: `4.728962024742951e-10`
- `S_ren_se`: `7.494135754866123e-11`
- `alpha_inv_half_RT_only`: `2.3644810123714757e-10`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `16.755160819618457`
- `alpha_inv_pred_blind_with_soft`: `8.377580409809228`
- `a_M`: `-1.6649302298967905e-13`
- `a_M_se`: `2.652539697737057e-14`
- `a_sqrtM`: `1.3635027124605686e-11`
- `a_sqrtM_se`: `2.159046860398579e-12`
- `a_logM`: `-1.0285454709728741e-10`
- `a_logM_se`: `1.6277634964561966e-11`
- `b_inv_sqrt`: `-1.3541050829631764e-09`
- `b_inv_sqrt_se`: `2.1551616125399294e-10`
- `b_inv`: `1.6436368756995853e-09`
- `b_inv_se`: `2.6423791299001406e-10`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `147`
- `M_min`: `49`
- `M_max`: `195`
- `rms`: `2.780559610005164e-15`
- `S_inf`: `1.756469305289656e-13`
- `S_inf_se`: `3.806266630155423e-14`
- `alpha_inv_pred_blind`: `8.78234652644828e-14`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=195, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=195, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=195, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.