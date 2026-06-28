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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C4_tube_boundary_only\runs\g001_nc24_nt5_ns96_tf0p32_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `90`
- `M_min`: `30`
- `M_max`: `119`
- `rms`: `0.0002846341563142758`
- `S_ren`: `-130.85820850616204`
- `S_ren_se`: `10.127742949011456`
- `alpha_inv_half_RT_only`: `-65.42910425308102`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-114.10304768701648`
- `alpha_inv_pred_blind_with_soft`: `-57.05152384350824`
- `a_M`: `0.09082248544135019`
- `a_M_se`: `0.006580904779078399`
- `a_sqrtM`: `-5.660242317444768`
- `a_sqrtM_se`: `0.41844188953101064`
- `a_logM`: `32.36537519674251`
- `a_logM_se`: `2.4642380816305924`
- `b_inv_sqrt`: `322.80087522732464`
- `b_inv_sqrt_se`: `25.483378029933323`
- `b_inv`: `-296.6649748437901`
- `b_inv_se`: `24.40195856486617`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `90`
- `M_min`: `30`
- `M_max`: `119`
- `rms`: `0.0005403918044449101`
- `S_inf`: `-0.25287258864170986`
- `S_inf_se`: `0.009455254293855846`
- `alpha_inv_pred_blind`: `-0.12643629432085493`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=119, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=119, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=119, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.