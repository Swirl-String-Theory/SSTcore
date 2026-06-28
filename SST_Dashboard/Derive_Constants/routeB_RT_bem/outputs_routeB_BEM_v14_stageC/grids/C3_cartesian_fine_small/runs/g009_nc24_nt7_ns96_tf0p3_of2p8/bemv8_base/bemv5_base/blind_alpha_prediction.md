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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g009_nc24_nt7_ns96_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0007331807493830103`
- `S_ren`: `247.47401338343735`
- `S_ren_se`: `20.970160085686125`
- `alpha_inv_half_RT_only`: `123.73700669171868`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `264.2291742025829`
- `alpha_inv_pred_blind_with_soft`: `132.11458710129145`
- `a_M`: `-0.07191853495129052`
- `a_M_se`: `0.00516688927656053`
- `a_sqrtM`: `6.3244724753646855`
- `a_sqrtM_se`: `0.48843125985377905`
- `a_logM`: `-51.8276458069896`
- `a_logM_se`: `4.276811826970192`
- `b_inv_sqrt`: `-748.7714080528008`
- `b_inv_sqrt_se`: `65.7672955134543`
- `b_inv`: `1004.3007461258569`
- `b_inv_se`: `93.65710191535489`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.002090418688805248`
- `S_inf`: `-0.6054045561155686`
- `S_inf_se`: `0.024660674462905496`
- `alpha_inv_pred_blind`: `-0.3027022780577843`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=263, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=263, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=263, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.