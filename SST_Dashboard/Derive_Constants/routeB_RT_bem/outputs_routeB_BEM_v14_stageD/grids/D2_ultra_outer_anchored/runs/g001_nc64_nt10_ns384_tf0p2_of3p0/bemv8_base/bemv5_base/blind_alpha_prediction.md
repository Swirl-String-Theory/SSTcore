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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D2_ultra_outer_anchored\runs\g001_nc64_nt10_ns384_tf0p2_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0008569454347074115`
- `S_ren`: `-66.49804372468674`
- `S_ren_se`: `15.926362866601243`
- `alpha_inv_half_RT_only`: `-33.24902186234337`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-49.74288290554118`
- `alpha_inv_pred_blind_with_soft`: `-24.87144145277059`
- `a_M`: `0.004621833082716811`
- `a_M_se`: `0.0007897162759395646`
- `a_sqrtM`: `-0.7815056284939073`
- `a_sqrtM_se`: `0.14724994070811318`
- `a_logM`: `11.40963331574675`
- `a_logM_se`: `2.5433801714445057`
- `b_inv_sqrt`: `263.94252154938744`
- `b_inv_sqrt_se`: `77.15628395465183`
- `b_inv`: `-480.5818298217597`
- `b_inv_se`: `216.77211417279153`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0009022337337397883`
- `S_inf`: `-0.3866295556692856`
- `S_inf_se`: `0.00540888855512995`
- `alpha_inv_pred_blind`: `-0.1933147778346428`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.