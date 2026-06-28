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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B1_paired_coarse\runs\g001_nc12_nt4_ns24_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0018067626532398445`
- `S_ren`: `561.8934825971673`
- `S_ren_se`: `73.13374417092903`
- `alpha_inv_half_RT_only`: `280.9467412985837`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `578.6486434163129`
- `alpha_inv_pred_blind_with_soft`: `289.32432170815645`
- `a_M`: `-0.7763130111679768`
- `a_M_se`: `0.09106985661419434`
- `a_sqrtM`: `36.565695114828564`
- `a_sqrtM_se`: `4.473618886222655`
- `a_logM`: `-159.88488147315496`
- `a_logM_se`: `20.351344975160305`
- `b_inv_sqrt`: `-1228.069122688544`
- `b_inv_sqrt_se`: `162.5560379906696`
- `b_inv`: `873.6498837134275`
- `b_inv_se`: `120.21350208639862`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.004183308433540017`
- `S_inf`: `-0.9662510269792495`
- `S_inf_se`: `0.09470428165938599`
- `alpha_inv_pred_blind`: `-0.48312551348962474`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.