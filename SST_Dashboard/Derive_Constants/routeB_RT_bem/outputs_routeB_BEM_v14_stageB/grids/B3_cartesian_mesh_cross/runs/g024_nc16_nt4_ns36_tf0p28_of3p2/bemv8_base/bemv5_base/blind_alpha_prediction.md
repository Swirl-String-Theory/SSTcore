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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g024_nc16_nt4_ns36_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `75`
- `M_min`: `25`
- `M_max`: `99`
- `rms`: `0.0009306481374659638`
- `S_ren`: `183.71919035625388`
- `S_ren_se`: `34.70221425637145`
- `alpha_inv_half_RT_only`: `91.85959517812694`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `200.47435117539945`
- `alpha_inv_pred_blind_with_soft`: `100.23717558769972`
- `a_M`: `-0.17018287118616726`
- `a_M_se`: `0.02837455555386025`
- `a_sqrtM`: `9.370636189631881`
- `a_sqrtM_se`: `1.6456379346904013`
- `a_logM`: `-47.95848594835204`
- `a_logM_se`: `8.839390507773611`
- `b_inv_sqrt`: `-432.07309561915474`
- `b_inv_sqrt_se`: `83.37219492013388`
- `b_inv`: `361.99544382357095`
- `b_inv_se`: `72.81099855625732`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `75`
- `M_min`: `25`
- `M_max`: `99`
- `rms`: `0.0016320250526303353`
- `S_inf`: `-0.3578588383655323`
- `S_inf_se`: `0.03129358438799317`
- `alpha_inv_pred_blind`: `-0.17892941918276614`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=99, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=99, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=99, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.