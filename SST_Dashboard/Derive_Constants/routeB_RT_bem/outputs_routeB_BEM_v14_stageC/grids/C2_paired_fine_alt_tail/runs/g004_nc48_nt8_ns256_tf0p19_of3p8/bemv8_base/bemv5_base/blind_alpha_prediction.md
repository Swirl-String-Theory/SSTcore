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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C2_paired_fine_alt_tail\runs\g004_nc48_nt8_ns256_tf0p19_of3p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0006284382215227712`
- `S_ren`: `-59.95259248120439`
- `S_ren_se`: `13.65438863701521`
- `alpha_inv_half_RT_only`: `-29.976296240602196`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-43.19743166205883`
- `alpha_inv_pred_blind_with_soft`: `-21.598715831029416`
- `a_M`: `0.005990545613922094`
- `a_M_se`: `0.0011721089827390514`
- `a_sqrtM`: `-0.8533162340994371`
- `a_sqrtM_se`: `0.17272367587467405`
- `a_logM`: `10.753250876974004`
- `a_logM_se`: `2.357770838306279`
- `b_inv_sqrt`: `225.75884034210776`
- `b_inv_sqrt_se`: `56.5260598690694`
- `b_inv`: `-414.8253036963351`
- `b_inv_se`: `125.50510036176703`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0006669474996320266`
- `S_inf`: `-0.2838199362630793`
- `S_inf_se`: `0.005056412120398451`
- `alpha_inv_pred_blind`: `-0.14190996813153964`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=639, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=639, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=639, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.