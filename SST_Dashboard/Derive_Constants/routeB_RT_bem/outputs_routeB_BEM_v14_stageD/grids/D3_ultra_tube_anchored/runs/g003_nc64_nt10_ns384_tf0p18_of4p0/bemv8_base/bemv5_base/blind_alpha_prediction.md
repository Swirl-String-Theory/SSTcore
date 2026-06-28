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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D3_ultra_tube_anchored\runs\g003_nc64_nt10_ns384_tf0p18_of4p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0006250416389197649`
- `S_ren`: `73.18686666552772`
- `S_ren_se`: `11.616422172282364`
- `alpha_inv_half_RT_only`: `36.59343333276386`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `89.94202748467328`
- `alpha_inv_pred_blind_with_soft`: `44.97101374233664`
- `a_M`: `-0.0025241683230698003`
- `a_M_se`: `0.0005760058171771594`
- `a_sqrtM`: `0.5446536235644344`
- `a_sqrtM_se`: `0.10740163905822282`
- `a_logM`: `-11.084002188414201`
- `a_logM_se`: `1.855098873708904`
- `b_inv_sqrt`: `-396.8931832846967`
- `b_inv_sqrt_se`: `56.27650048971926`
- `b_inv`: `1297.4121534311794`
- `b_inv_se`: `158.10994729311457`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0006763568372778303`
- `S_inf`: `-0.2320155945799884`
- `S_inf_se`: `0.004054757231446017`
- `alpha_inv_pred_blind`: `-0.1160077972899942`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.