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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g015_nc24_nt7_ns144_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `234`
- `M_min`: `78`
- `M_max`: `311`
- `rms`: `0.002077820672552787`
- `S_ren`: `1111.2295319215461`
- `S_ren_se`: `56.54329985541928`
- `alpha_inv_half_RT_only`: `555.6147659607731`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `1127.9846927406918`
- `alpha_inv_pred_blind_with_soft`: `563.9923463703459`
- `a_M`: `-0.2579225766477604`
- `a_M_se`: `0.01139139332882639`
- `a_sqrtM`: `24.932040070719204`
- `a_sqrtM_se`: `1.1710115980040945`
- `a_logM`: `-224.0983781347184`
- `a_logM_se`: `11.150494316704735`
- `b_inv_sqrt`: `-3549.7383441570614`
- `b_inv_sqrt_se`: `186.46898205667756`
- `b_inv`: `5223.5110513772115`
- `b_inv_se`: `288.7795879473023`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `234`
- `M_min`: `78`
- `M_max`: `311`
- `rms`: `0.007385791239208353`
- `S_inf`: `-1.69221336357049`
- `S_inf_se`: `0.08015804133608888`
- `alpha_inv_pred_blind`: `-0.846106681785245`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=311, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=311, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=311, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.