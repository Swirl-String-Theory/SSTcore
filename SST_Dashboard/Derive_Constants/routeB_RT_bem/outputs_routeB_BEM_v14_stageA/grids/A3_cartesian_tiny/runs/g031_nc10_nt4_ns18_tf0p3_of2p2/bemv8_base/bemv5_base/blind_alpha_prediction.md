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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g031_nc10_nt4_ns18_tf0p3_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.039016675876594784`
- `S_ren`: `23150.900177049578`
- `S_ren_se`: `1906.0496118483102`
- `alpha_inv_half_RT_only`: `11575.450088524789`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `23167.655337868724`
- `alpha_inv_pred_blind_with_soft`: `11583.827668934362`
- `a_M`: `-43.580577744190236`
- `a_M_se`: `3.085759146073461`
- `a_sqrtM`: `1820.4500608442513`
- `a_sqrtM_se`: `136.8299772865821`
- `a_logM`: `-7063.042451691766`
- `a_logM_se`: `562.1891345972923`
- `b_inv_sqrt`: `-48256.101777151576`
- `b_inv_sqrt_se`: `4057.8636422229306`
- `b_inv`: `30608.67492388718`
- `b_inv_se`: `2713.262271892922`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `43`
- `M_min`: `15`
- `M_max`: `57`
- `rms`: `0.20438137654362465`
- `S_inf`: `-40.09667287070089`
- `S_inf_se`: `5.595499082677671`
- `alpha_inv_pred_blind`: `-20.048336435350446`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=57, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=57, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=57, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.