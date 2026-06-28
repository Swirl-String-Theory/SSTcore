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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g032_nc10_nt4_ns18_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.024669802671471737`
- `S_ren`: `14436.356655113883`
- `S_ren_se`: `1205.1736020530764`
- `alpha_inv_half_RT_only`: `7218.178327556941`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `14453.111815933029`
- `alpha_inv_pred_blind_with_soft`: `7226.5559079665145`
- `a_M`: `-26.767758340838952`
- `a_M_se`: `1.9510905917791705`
- `a_sqrtM`: `1124.3748151934733`
- `a_sqrtM_se`: `86.51604636639142`
- `a_logM`: `-4388.207665686226`
- `a_logM_se`: `355.465828468499`
- `b_inv_sqrt`: `-30164.64347627695`
- `b_inv_sqrt_se`: `2565.741265042802`
- `b_inv`: `19249.026649619253`
- `b_inv_se`: `1715.5650331478046`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.11760941953308464`
- `S_inf`: `-23.92577681952578`
- `S_inf_se`: `3.219879473564277`
- `alpha_inv_pred_blind`: `-11.96288840976289`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=57, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=57, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=57, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.