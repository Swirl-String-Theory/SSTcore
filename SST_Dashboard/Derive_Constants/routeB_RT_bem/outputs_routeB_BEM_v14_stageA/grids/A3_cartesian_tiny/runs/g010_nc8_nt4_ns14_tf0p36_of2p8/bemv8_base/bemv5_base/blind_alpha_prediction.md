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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g010_nc8_nt4_ns14_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.03424085280761882`
- `S_ren`: `18289.92614104721`
- `S_ren_se`: `1840.3624024789394`
- `alpha_inv_half_RT_only`: `9144.963070523605`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `18306.681301866356`
- `alpha_inv_pred_blind_with_soft`: `9153.340650933178`
- `a_M`: `-46.9715963544312`
- `a_M_se`: `4.031025952876585`
- `a_sqrtM`: `1743.3624844928759`
- `a_sqrtM_se`: `159.19312824910523`
- `a_logM`: `-6011.876082659866`
- `a_logM_se`: `582.5756111825414`
- `b_inv_sqrt`: `-36515.89808454388`
- `b_inv_sqrt_se`: `3745.6801446665586`
- `b_inv`: `20592.93792306384`
- `b_inv_se`: `2231.121333650203`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `34`
- `M_min`: `12`
- `M_max`: `45`
- `rms`: `0.17733914739304085`
- `S_inf`: `-36.85678045810075`
- `S_inf_se`: `5.595428462112865`
- `alpha_inv_pred_blind`: `-18.428390229050375`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=45, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=45, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=45, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.