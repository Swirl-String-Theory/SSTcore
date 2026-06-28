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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g024_nc32_nt5_ns144_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `228`
- `M_min`: `76`
- `M_max`: `303`
- `rms`: `0.0005612045918732784`
- `S_ren`: `-130.0553341433822`
- `S_ren_se`: `15.392412718808425`
- `alpha_inv_half_RT_only`: `-65.0276670716911`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-113.30017332423664`
- `alpha_inv_pred_blind_with_soft`: `-56.65008666211832`
- `a_M`: `0.024198113219736306`
- `a_M_se`: `0.0031993499488682645`
- `a_sqrtM`: `-2.6080409906184148`
- `a_sqrtM_se`: `0.32462810154198096`
- `a_logM`: `25.493146701285628`
- `a_logM_se`: `3.0511116978430843`
- `b_inv_sqrt`: `429.21441370576895`
- `b_inv_sqrt_se`: `50.36266191395985`
- `b_inv`: `-658.4581800003406`
- `b_inv_se`: `76.98491990055997`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `228`
- `M_min`: `76`
- `M_max`: `303`
- `rms`: `0.0009844483524928018`
- `S_inf`: `-0.2492299967372978`
- `S_inf_se`: `0.010823681848290505`
- `alpha_inv_pred_blind`: `-0.1246149983686489`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=303, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=303, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=303, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.