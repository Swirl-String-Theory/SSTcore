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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g031_nc32_nt7_ns144_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `276`
- `M_min`: `92`
- `M_max`: `367`
- `rms`: `0.0006568451963312653`
- `S_ren`: `73.43278243560812`
- `S_ren_se`: `17.002922674665157`
- `alpha_inv_half_RT_only`: `36.71639121780406`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `90.18794325475368`
- `alpha_inv_pred_blind_with_soft`: `45.09397162737684`
- `a_M`: `-0.015274582826347305`
- `a_M_se`: `0.002810832225409791`
- `a_sqrtM`: `1.5155184746209476`
- `a_sqrtM_se`: `0.3138917973175197`
- `a_logM`: `-14.391609008680538`
- `a_logM_se`: `3.2469721635413253`
- `b_inv_sqrt`: `-248.35159742763005`
- `b_inv_sqrt_se`: `58.987755661186135`
- `b_inv`: `407.84952175365277`
- `b_inv_se`: `99.24253195820329`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `276`
- `M_min`: `92`
- `M_max`: `367`
- `rms`: `0.0012691175414171344`
- `S_inf`: `-0.5231169879778442`
- `S_inf_se`: `0.012684085107498399`
- `alpha_inv_pred_blind`: `-0.2615584939889221`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=367, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=367, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=367, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.