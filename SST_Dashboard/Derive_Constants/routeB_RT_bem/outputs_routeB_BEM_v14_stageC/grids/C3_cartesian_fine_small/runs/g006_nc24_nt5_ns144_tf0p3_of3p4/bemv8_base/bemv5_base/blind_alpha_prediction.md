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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g006_nc24_nt5_ns144_tf0p3_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0005573168316611723`
- `S_ren`: `-3.191996290074177`
- `S_ren_se`: `15.940166443564003`
- `alpha_inv_half_RT_only`: `-1.5959981450370886`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `13.563164529071384`
- `alpha_inv_pred_blind_with_soft`: `6.781582264535692`
- `a_M`: `-0.0027920788831039857`
- `a_M_se`: `0.003927536782137353`
- `a_sqrtM`: `0.09454424813004497`
- `a_sqrtM_se`: `0.37127401729390075`
- `a_logM`: `0.27389744475723177`
- `a_logM_se`: `3.250957173962716`
- `b_inv_sqrt`: `16.0858028813062`
- `b_inv_sqrt_se`: `49.99206647655026`
- `b_inv`: `-33.639960739982044`
- `b_inv_se`: `71.19210282861067`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0009239240699310194`
- `S_inf`: `-0.296645041724751`
- `S_inf_se`: `0.01089953454732738`
- `alpha_inv_pred_blind`: `-0.1483225208623755`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=263, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=263, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=263, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.