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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g012_nc8_nt4_ns14_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `34`
- `M_min`: `12`
- `M_max`: `45`
- `rms`: `0.019715478198419352`
- `S_ren`: `10913.17143309496`
- `S_ren_se`: `1059.658911742725`
- `alpha_inv_half_RT_only`: `5456.58571654748`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `10929.926593914106`
- `alpha_inv_pred_blind_with_soft`: `5464.963296957053`
- `a_M`: `-27.753938662770622`
- `a_M_se`: `2.321017082656233`
- `a_sqrtM`: `1033.8923950759702`
- `a_sqrtM_se`: `91.66152101898166`
- `a_logM`: `-3578.5364297011915`
- `a_logM_se`: `335.44014881091294`
- `b_inv_sqrt`: `-21813.78649308237`
- `b_inv_sqrt_se`: `2156.718340087433`
- `b_inv`: `12341.865625525503`
- `b_inv_se`: `1284.6532841559756`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `34`
- `M_min`: `12`
- `M_max`: `45`
- `rms`: `0.09998394077110756`
- `S_inf`: `-20.91921375273418`
- `S_inf_se`: `3.1547066520227127`
- `alpha_inv_pred_blind`: `-10.45960687636709`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=45, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=45, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=45, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.