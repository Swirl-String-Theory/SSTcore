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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C2_paired_fine_alt_tail\runs\g002_nc32_nt6_ns144_tf0p29_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `252`
- `M_min`: `84`
- `M_max`: `335`
- `rms`: `0.00045370270525274536`
- `S_ren`: `-91.37109044072892`
- `S_ren_se`: `12.073710982779613`
- `alpha_inv_half_RT_only`: `-45.68554522036446`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-74.61592962158336`
- `alpha_inv_pred_blind_with_soft`: `-37.30796481079168`
- `a_M`: `0.014097832941929789`
- `a_M_se`: `0.002225461579899578`
- `a_sqrtM`: `-1.6585005227127847`
- `a_sqrtM_se`: `0.2374379839509392`
- `a_logM`: `17.44615631953777`
- `a_logM_se`: `2.3465576582630834`
- `b_inv_sqrt`: `313.46830931446465`
- `b_inv_sqrt_se`: `40.72811075963385`
- `b_inv`: `-511.5125922304639`
- `b_inv_se`: `65.46470304665833`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `252`
- `M_min`: `84`
- `M_max`: `335`
- `rms`: `0.0009343750531914037`
- `S_inf`: `-0.2884340093084265`
- `S_inf_se`: `0.00977244489367916`
- `alpha_inv_pred_blind`: `-0.14421700465421325`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=335, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=335, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=335, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.