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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D2_ultra_outer_anchored\runs\g003_nc64_nt10_ns384_tf0p2_of4p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0005769938359212516`
- `S_ren`: `67.91547310407121`
- `S_ren_se`: `10.723451961456089`
- `alpha_inv_half_RT_only`: `33.957736552035605`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `84.67063392321677`
- `alpha_inv_pred_blind_with_soft`: `42.335316961608385`
- `a_M`: `-0.002182873025411272`
- `a_M_se`: `0.000531727464654027`
- `a_sqrtM`: `0.49017504713582183`
- `a_sqrtM_se`: `0.09914552862675548`
- `a_logM`: `-10.226757823773054`
- `a_logM_se`: `1.7124948939472115`
- `b_inv_sqrt`: `-371.5471614068451`
- `b_inv_sqrt_se`: `51.95044916672433`
- `b_inv`: `1224.889236675451`
- `b_inv_se`: `145.95582006924803`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.000673122676479347`
- `S_inf`: `-0.1766253802065991`
- `S_inf_se`: `0.004035368447061004`
- `alpha_inv_pred_blind`: `-0.08831269010329955`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.