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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g016_nc12_nt5_ns36_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `0.013344106689010364`
- `S_ren`: `7180.73393483823`
- `S_ren_se`: `502.7528853635364`
- `alpha_inv_half_RT_only`: `3590.366967419115`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `7197.489095657375`
- `alpha_inv_pred_blind_with_soft`: `3598.7445478286877`
- `a_M`: `-7.685843436067174`
- `a_M_se`: `0.43293140781344536`
- `a_sqrtM`: `399.14676896869247`
- `a_sqrtM_se`: `24.596485254121966`
- `a_logM`: `-1929.8274492637797`
- `a_logM_se`: `129.42140602012057`
- `b_inv_sqrt`: `-16478.033354570005`
- `b_inv_sqrt_se`: `1195.765856943845`
- `b_inv`: `13095.75672732443`
- `b_inv_se`: `1022.9607105886311`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `0.09314253638897249`
- `S_inf`: `-22.435684769594722`
- `S_inf_se`: `1.8230541812823922`
- `alpha_inv_pred_blind`: `-11.217842384797361`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=95, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=95, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=95, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.