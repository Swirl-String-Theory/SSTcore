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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g010_nc12_nt5_ns24_tf0p32_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0022766056053928553`
- `S_ren`: `-357.55904271712154`
- `S_ren_se`: `88.69365116170307`
- `alpha_inv_half_RT_only`: `-178.77952135856077`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-340.803881897976`
- `alpha_inv_pred_blind_with_soft`: `-170.401940948988`
- `a_M`: `0.3013639342109631`
- `a_M_se`: `0.09055959296369195`
- `a_sqrtM`: `-17.645024564455202`
- `a_sqrtM_se`: `4.809357680536611`
- `a_logM`: `92.70151733429127`
- `a_logM_se`: `23.654072335791515`
- `b_inv_sqrt`: `836.7430618191646`
- `b_inv_sqrt_se`: `204.276359988279`
- `b_inv`: `-687.1576930164572`
- `b_inv_se`: `163.33860516948536`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `63`
- `M_min`: `21`
- `M_max`: `83`
- `rms`: `0.004832269196634835`
- `S_inf`: `-1.7822184723490009`
- `S_inf_se`: `0.10117152399958067`
- `alpha_inv_pred_blind`: `-0.8911092361745004`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=83, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=83, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=83, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.