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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g018_nc16_nt4_ns24_tf0p32_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `66`
- `M_min`: `22`
- `M_max`: `87`
- `rms`: `0.0008739049692502088`
- `S_ren`: `186.85478229605502`
- `S_ren_se`: `33.65299428342821`
- `alpha_inv_half_RT_only`: `93.42739114802751`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `203.6099431152006`
- `alpha_inv_pred_blind_with_soft`: `101.8049715576003`
- `a_M`: `-0.1871411432089123`
- `a_M_se`: `0.032375881238409086`
- `a_sqrtM`: `9.971019555573013`
- `a_sqrtM_se`: `1.7602973575028151`
- `a_logM`: `-49.51616160810518`
- `a_logM_se`: `8.863828247093766`
- `b_inv_sqrt`: `-434.1842995678861`
- `b_inv_sqrt_se`: `78.37090856431402`
- `b_inv`: `354.96515452033384`
- `b_inv_se`: `64.15819041375565`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `66`
- `M_min`: `22`
- `M_max`: `87`
- `rms`: `0.001221902992194358`
- `S_inf`: `-0.3361052643621207`
- `S_inf_se`: `0.02498841287679665`
- `alpha_inv_pred_blind`: `-0.16805263218106034`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=87, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=87, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=87, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.