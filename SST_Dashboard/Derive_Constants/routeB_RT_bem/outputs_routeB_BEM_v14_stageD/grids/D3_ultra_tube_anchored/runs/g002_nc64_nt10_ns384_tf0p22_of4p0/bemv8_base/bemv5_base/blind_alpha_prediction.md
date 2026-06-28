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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D3_ultra_tube_anchored\runs\g002_nc64_nt10_ns384_tf0p22_of4p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0006667489574617719`
- `S_ren`: `22.76093913149613`
- `S_ren_se`: `12.391554242995507`
- `alpha_inv_half_RT_only`: `11.380469565748065`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `39.51609995064169`
- `alpha_inv_pred_blind_with_soft`: `19.758049975320844`
- `a_M`: `0.0002264718204853869`
- `a_M_se`: `0.0006144411094891661`
- `a_sqrtM`: `0.05071389652905061`
- `a_sqrtM_se`: `0.11456825659729845`
- `a_logM`: `-2.909335260051919`
- `a_logM_se`: `1.9788845462705167`
- `b_inv_sqrt`: `-160.87385518454738`
- `b_inv_sqrt_se`: `60.031677403069565`
- `b_inv`: `669.9824087620705`
- `b_inv_se`: `168.66019151014083`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0007549611922340453`
- `S_inf`: `-0.2260757177785146`
- `S_inf_se`: `0.0045259901060402`
- `alpha_inv_pred_blind`: `-0.1130378588892573`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.