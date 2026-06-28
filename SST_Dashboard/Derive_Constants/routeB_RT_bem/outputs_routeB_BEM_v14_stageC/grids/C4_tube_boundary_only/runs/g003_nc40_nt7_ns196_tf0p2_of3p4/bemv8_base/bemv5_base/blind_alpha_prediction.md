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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C4_tube_boundary_only\runs\g003_nc40_nt7_ns196_tf0p2_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `210`
- `M_min`: `70`
- `M_max`: `279`
- `rms`: `0.00020691898176281205`
- `S_ren`: `-5.28738995561125`
- `S_ren_se`: `5.815849177568215`
- `alpha_inv_half_RT_only`: `-2.643694977805625`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `11.467770863534312`
- `alpha_inv_pred_blind_with_soft`: `5.733885431767156`
- `a_M`: `3.861837230178383e-05`
- `a_M_se`: `0.0013346973325985482`
- `a_sqrtM`: `-0.06468903012128491`
- `a_sqrtM_se`: `0.12995230153663087`
- `a_logM`: `0.9491715110720386`
- `a_logM_se`: `1.1720061285602952`
- `b_inv_sqrt`: `18.92410471124808`
- `b_inv_sqrt_se`: `18.56313634468519`
- `b_inv`: `-31.907944778959568`
- `b_inv_se`: `27.22802728264483`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `210`
- `M_min`: `70`
- `M_max`: `279`
- `rms`: `0.00035933737864318977`
- `S_inf`: `-0.15773626657336054`
- `S_inf_se`: `0.004116381535242693`
- `alpha_inv_pred_blind`: `-0.07886813328668027`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=279, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=279, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=279, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.