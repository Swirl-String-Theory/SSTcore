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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D2_ultra_outer_anchored\runs\g004_nc64_nt10_ns384_tf0p2_of5p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0005229587060023062`
- `S_ren`: `65.90208583723769`
- `S_ren_se`: `9.719207056496769`
- `alpha_inv_half_RT_only`: `32.951042918618846`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `82.65724665638325`
- `alpha_inv_pred_blind_with_soft`: `41.328623328191625`
- `a_M`: `-0.002263103889165105`
- `a_M_se`: `0.00048193150350969835`
- `a_sqrtM`: `0.49366133566295517`
- `a_sqrtM_se`: `0.0898606087771777`
- `a_logM`: `-10.00783420832957`
- `a_logM_se`: `1.5521207645906592`
- `b_inv_sqrt`: `-354.3051950524225`
- `b_inv_sqrt_se`: `47.08532046809706`
- `b_inv`: `1143.445551923044`
- `b_inv_se`: `132.2871442379443`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0006129964074705175`
- `S_inf`: `-0.12719467817797733`
- `S_inf_se`: `0.00367491164286184`
- `alpha_inv_pred_blind`: `-0.06359733908898867`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.