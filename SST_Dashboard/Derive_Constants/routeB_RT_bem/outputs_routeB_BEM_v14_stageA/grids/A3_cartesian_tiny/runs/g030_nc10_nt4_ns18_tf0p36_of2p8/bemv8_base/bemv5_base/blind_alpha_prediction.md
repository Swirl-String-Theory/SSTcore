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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g030_nc10_nt4_ns18_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0022078016995442673`
- `S_ren`: `245.40654129078132`
- `S_ren_se`: `107.85592257434676`
- `alpha_inv_half_RT_only`: `122.70327064539066`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `262.16170210992686`
- `alpha_inv_pred_blind_with_soft`: `131.08085105496343`
- `a_M`: `-0.5716593233274052`
- `a_M_se`: `0.17461108959238794`
- `a_sqrtM`: `22.173420671759814`
- `a_sqrtM_se`: `7.742675397499417`
- `a_logM`: `-79.16864315514283`
- `a_logM_se`: `31.81209313563772`
- `b_inv_sqrt`: `-492.04966571624334`
- `b_inv_sqrt_se`: `229.6186962250403`
- `b_inv`: `281.10472978611494`
- `b_inv_se`: `153.53294253311836`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.005587834753040103`
- `S_inf`: `-1.114063420303688`
- `S_inf_se`: `0.15298225681593108`
- `alpha_inv_pred_blind`: `-0.557031710151844`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=57, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=57, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=57, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.