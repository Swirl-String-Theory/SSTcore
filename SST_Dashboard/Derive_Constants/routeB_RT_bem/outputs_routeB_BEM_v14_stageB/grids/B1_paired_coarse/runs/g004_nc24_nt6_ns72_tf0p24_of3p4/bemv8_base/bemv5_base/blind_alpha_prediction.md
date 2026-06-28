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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B1_paired_coarse\runs\g004_nc24_nt6_ns72_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0006451971959137515`
- `S_ren`: `242.73955396851008`
- `S_ren_se`: `19.558341745442238`
- `alpha_inv_half_RT_only`: `121.36977698425504`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `259.49471478765565`
- `alpha_inv_pred_blind_with_soft`: `129.74735739382783`
- `a_M`: `-0.08721259401301529`
- `a_M_se`: `0.0061480530375947725`
- `a_sqrtM`: `7.036078630486118`
- `a_sqrtM_se`: `0.5254651368026412`
- `a_logM`: `-52.797650315773566`
- `a_logM_se`: `4.159910535827879`
- `b_inv_sqrt`: `-697.8953721873244`
- `b_inv_sqrt_se`: `57.83467296435281`
- `b_inv`: `856.6579398741021`
- `b_inv_se`: `74.46022536493669`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0017195143409370764`
- `S_inf`: `-0.40790950236618295`
- `S_inf_se`: `0.022423087191138776`
- `alpha_inv_pred_blind`: `-0.20395475118309148`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.