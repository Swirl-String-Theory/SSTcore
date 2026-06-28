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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C2_paired_fine_alt_tail\runs\g003_nc40_nt7_ns196_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `357`
- `M_min`: `119`
- `M_max`: `475`
- `rms`: `0.0005077664695404355`
- `S_ren`: `-142.65019771215833`
- `S_ren_se`: `12.132521899866946`
- `alpha_inv_half_RT_only`: `-71.32509885607917`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-125.89503689301277`
- `alpha_inv_pred_blind_with_soft`: `-62.947518446506386`
- `a_M`: `0.017335993278407402`
- `a_M_se`: `0.001476785996290897`
- `a_sqrtM`: `-2.234952764144722`
- `a_sqrtM_se`: `0.18762354795842537`
- `a_logM`: `26.13395709609551`
- `a_logM_se`: `2.208091884090869`
- `b_inv_sqrt`: `525.9583729800138`
- `b_inv_sqrt_se`: `45.63923200574025`
- `b_inv`: `-964.7338703912518`
- `b_inv_se`: `87.36127328051404`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `357`
- `M_min`: `119`
- `M_max`: `475`
- `rms`: `0.0007479906935926893`
- `S_inf`: `-0.30591364381072744`
- `S_inf_se`: `0.006574360656522565`
- `alpha_inv_pred_blind`: `-0.15295682190536372`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=475, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=475, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=475, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.