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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g021_nc10_nt3_ns18_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0016436424109188968`
- `S_ren`: `-337.2315601753336`
- `S_ren_se`: `73.66065448328906`
- `alpha_inv_half_RT_only`: `-168.6157800876668`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-320.47639935618804`
- `alpha_inv_pred_blind_with_soft`: `-160.23819967809402`
- `a_M`: `0.7604557333767445`
- `a_M_se`: `0.15631665012792456`
- `a_sqrtM`: `-29.733301792963378`
- `a_sqrtM_se`: `6.251333921188124`
- `a_logM`: `107.52643732220328`
- `a_logM_se`: `23.149401638455657`
- `b_inv_sqrt`: `684.7699303178264`
- `b_inv_sqrt_se`: `150.4971333772346`
- `b_inv`: `-405.1313865833792`
- `b_inv_se`: `90.57291393377808`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.002395203562320804`
- `S_inf`: `-0.32769668151890796`
- `S_inf_se`: `0.06683507642391995`
- `alpha_inv_pred_blind`: `-0.16384834075945398`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.