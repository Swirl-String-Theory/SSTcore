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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g030_nc16_nt5_ns36_tf0p32_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `87`
- `M_min`: `29`
- `M_max`: `115`
- `rms`: `0.001021466150069732`
- `S_ren`: `-45.84601252794137`
- `S_ren_se`: `36.66734602937213`
- `alpha_inv_half_RT_only`: `-22.923006263970684`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-29.090851708795807`
- `alpha_inv_pred_blind_with_soft`: `-14.545425854397903`
- `a_M`: `0.012534746618968473`
- `a_M_se`: `0.024861685875891965`
- `a_sqrtM`: `-1.3055065122657954`
- `a_sqrtM_se`: `1.554020882417596`
- `a_logM`: `10.094351951219435`
- `a_logM_se`: `8.996600109744058`
- `b_inv_sqrt`: `124.77939222766587`
- `b_inv_sqrt_se`: `91.45848463320489`
- `b_inv`: `-134.58625005970163`
- `b_inv_se`: `86.09145413504164`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `87`
- `M_min`: `29`
- `M_max`: `115`
- `rms`: `0.0017034676346139174`
- `S_inf`: `-0.468719538489211`
- `S_inf_se`: `0.030316768831191943`
- `alpha_inv_pred_blind`: `-0.2343597692446055`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=115, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=115, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=115, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.