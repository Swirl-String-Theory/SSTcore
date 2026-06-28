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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B5_tube_radius_sweep\runs\g005_nc20_nt5_ns64_tf0p18_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.008303133279341094`
- `S_ren`: `48.15943143948832`
- `S_ren_se`: `271.79850615356236`
- `alpha_inv_half_RT_only`: `24.07971571974416`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `64.91459225863389`
- `alpha_inv_pred_blind_with_soft`: `32.457296129316944`
- `a_M`: `-0.21905805417442814`
- `a_M_se`: `0.11975971946776744`
- `a_sqrtM`: `9.49528141225329`
- `a_sqrtM_se`: `8.91212242050593`
- `a_logM`: `-26.746581260080625`
- `a_logM_se`: `61.42863152868156`
- `b_inv_sqrt`: `62.18636226248417`
- `b_inv_sqrt_se`: `743.5491791140798`
- `b_inv`: `-425.04014734531927`
- `b_inv_se`: `833.4219111158358`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.02296814797906096`
- `S_inf`: `-6.946712021137094`
- `S_inf_se`: `0.34369960333889343`
- `alpha_inv_pred_blind`: `-3.473356010568547`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=163, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=163, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=163, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.