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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g008_nc24_nt5_ns144_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.000513592338507686`
- `S_ren`: `-58.33715298085863`
- `S_ren_se`: `14.689574932718008`
- `alpha_inv_half_RT_only`: `-29.168576490429317`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-41.581992161713075`
- `alpha_inv_pred_blind_with_soft`: `-20.790996080856537`
- `a_M`: `0.00865834881920663`
- `a_M_se`: `0.003619400466518168`
- `a_sqrtM`: `-1.078214328870906`
- `a_sqrtM_se`: `0.3421455802810669`
- `a_logM`: `11.249551204762804`
- `a_logM_se`: `2.995902155668149`
- `b_inv_sqrt`: `194.47592403954243`
- `b_inv_sqrt_se`: `46.06992085990487`
- `b_inv`: `-299.5162759427268`
- `b_inv_se`: `65.60670070925681`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0011846002075301724`
- `S_inf`: `-0.35677398013364126`
- `S_inf_se`: `0.013974731589913317`
- `alpha_inv_pred_blind`: `-0.17838699006682063`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=263, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=263, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=263, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.