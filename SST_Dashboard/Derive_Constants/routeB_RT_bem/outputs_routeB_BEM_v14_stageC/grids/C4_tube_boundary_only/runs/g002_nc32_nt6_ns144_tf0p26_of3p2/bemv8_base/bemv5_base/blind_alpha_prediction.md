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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C4_tube_boundary_only\runs\g002_nc32_nt6_ns144_tf0p26_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `144`
- `M_min`: `48`
- `M_max`: `191`
- `rms`: `0.00025157291784274087`
- `S_ren`: `65.02204237914835`
- `S_ren_se`: `7.884132827529218`
- `alpha_inv_half_RT_only`: `32.51102118957417`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `81.7772031982939`
- `alpha_inv_pred_blind_with_soft`: `40.88860159914695`
- `a_M`: `-0.02363987869783024`
- `a_M_se`: `0.002861927387220124`
- `a_sqrtM`: `1.8918650052839`
- `a_sqrtM_se`: `0.23054585416532378`
- `a_logM`: `-14.153524199978445`
- `a_logM_se`: `1.7202201682882736`
- `b_inv_sqrt`: `-186.74231850889765`
- `b_inv_sqrt_se`: `22.540781254917388`
- `b_inv`: `228.28360380055025`
- `b_inv_se`: `27.35139789968029`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `144`
- `M_min`: `48`
- `M_max`: `191`
- `rms`: `0.00032146067177993515`
- `S_inf`: `-0.14436953063022206`
- `S_inf_se`: `0.004445990165810177`
- `alpha_inv_pred_blind`: `-0.07218476531511103`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=191, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=191, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=191, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.