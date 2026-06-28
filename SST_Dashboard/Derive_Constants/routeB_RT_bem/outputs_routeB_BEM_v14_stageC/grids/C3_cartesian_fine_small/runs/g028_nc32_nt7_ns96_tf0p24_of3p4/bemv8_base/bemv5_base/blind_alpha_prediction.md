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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g028_nc32_nt7_ns96_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `240`
- `M_min`: `80`
- `M_max`: `319`
- `rms`: `0.0005447427946402104`
- `S_ren`: `164.2211882766437`
- `S_ren_se`: `14.711712785172168`
- `alpha_inv_half_RT_only`: `82.11059413832184`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `180.97634909578926`
- `alpha_inv_pred_blind_with_soft`: `90.48817454789463`
- `a_M`: `-0.03448256752632295`
- `a_M_se`: `0.002875112347344925`
- `a_sqrtM`: `3.467541401447081`
- `a_sqrtM_se`: `0.29933365648421567`
- `a_logM`: `-32.53440808192833`
- `a_logM_se`: `2.88672674296705`
- `b_inv_sqrt`: `-538.4454743479639`
- `b_inv_sqrt_se`: `48.89181980541222`
- `b_inv`: `825.8441292433629`
- `b_inv_se`: `76.68580914236134`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `240`
- `M_min`: `80`
- `M_max`: `319`
- `rms`: `0.0008933200099718371`
- `S_inf`: `-0.25579076430283526`
- `S_inf_se`: `0.00957343361368018`
- `alpha_inv_pred_blind`: `-0.12789538215141763`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=319, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=319, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=319, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.