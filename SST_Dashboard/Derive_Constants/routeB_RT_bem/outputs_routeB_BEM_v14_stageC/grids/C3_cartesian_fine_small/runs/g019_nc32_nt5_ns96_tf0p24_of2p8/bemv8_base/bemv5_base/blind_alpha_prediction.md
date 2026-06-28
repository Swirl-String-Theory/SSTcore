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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g019_nc32_nt5_ns96_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `192`
- `M_min`: `64`
- `M_max`: `255`
- `rms`: `0.0007765393878392891`
- `S_ren`: `62.210625446270505`
- `S_ren_se`: `22.411540086207292`
- `alpha_inv_half_RT_only`: `31.105312723135253`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `78.96578626541607`
- `alpha_inv_pred_blind_with_soft`: `39.482893132708035`
- `a_M`: `-0.01364298928522939`
- `a_M_se`: `0.005731451705260173`
- `a_sqrtM`: `1.319201799257127`
- `a_sqrtM_se`: `0.5334941687160633`
- `a_logM`: `-12.292488483678795`
- `a_logM_se`: `4.599767640865325`
- `b_inv_sqrt`: `-206.2389712915615`
- `b_inv_sqrt_se`: `69.64885760963742`
- `b_inv`: `322.67044877233326`
- `b_inv_se`: `97.66336978208668`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `192`
- `M_min`: `64`
- `M_max`: `255`
- `rms`: `0.0007916567552119381`
- `S_inf`: `-0.3443130810704667`
- `S_inf_se`: `0.00948377131593363`
- `alpha_inv_pred_blind`: `-0.17215654053523335`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=255, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=255, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=255, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.