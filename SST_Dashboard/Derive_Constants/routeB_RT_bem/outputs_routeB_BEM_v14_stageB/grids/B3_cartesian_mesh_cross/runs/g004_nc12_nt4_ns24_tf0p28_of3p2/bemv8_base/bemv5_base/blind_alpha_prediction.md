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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g004_nc12_nt4_ns24_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0035748823857380215`
- `S_ren`: `845.5523069231734`
- `S_ren_se`: `144.70330863376478`
- `alpha_inv_half_RT_only`: `422.7761534615867`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `862.307467742319`
- `alpha_inv_pred_blind_with_soft`: `431.1537338711595`
- `a_M`: `-1.3343166190153717`
- `a_M_se`: `0.1801919171275634`
- `a_sqrtM`: `59.77154440896114`
- `a_sqrtM_se`: `8.851556306072993`
- `a_logM`: `-248.0322136701561`
- `a_logM_se`: `40.26741672311989`
- `b_inv_sqrt`: `-1807.4049871594748`
- `b_inv_sqrt_se`: `321.635338137058`
- `b_inv`: `1220.4014783594246`
- `b_inv_se`: `237.85588570027795`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0122790821596069`
- `S_inf`: `-2.2698737432694087`
- `S_inf_se`: `0.27798133315694695`
- `alpha_inv_pred_blind`: `-1.1349368716347044`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.