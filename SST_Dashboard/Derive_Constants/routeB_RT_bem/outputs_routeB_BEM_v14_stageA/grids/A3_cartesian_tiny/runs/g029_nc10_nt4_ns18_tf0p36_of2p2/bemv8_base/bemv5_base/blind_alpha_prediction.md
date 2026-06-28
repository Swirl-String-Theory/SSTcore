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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g029_nc10_nt4_ns18_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0030447877947557384`
- `S_ren`: `680.0389631633494`
- `S_ren_se`: `148.74451664489553`
- `alpha_inv_half_RT_only`: `340.0194815816747`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `696.794123982495`
- `alpha_inv_pred_blind_with_soft`: `348.3970619912475`
- `a_M`: `-1.3426537387924249`
- `a_M_se`: `0.24080682360632616`
- `a_sqrtM`: `55.099363200867735`
- `a_sqrtM_se`: `10.67795334786093`
- `a_logM`: `-209.91970861982648`
- `a_logM_se`: `43.87217970029488`
- `b_inv_sqrt`: `-1406.3333861723956`
- `b_inv_sqrt_se`: `316.6680249671174`
- `b_inv`: `874.566640357226`
- `b_inv_se`: `211.73787012405546`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.00821103528318957`
- `S_inf`: `-1.8694274128832813`
- `S_inf_se`: `0.2247995447134804`
- `alpha_inv_pred_blind`: `-0.9347137064416406`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=57, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=57, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=57, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.