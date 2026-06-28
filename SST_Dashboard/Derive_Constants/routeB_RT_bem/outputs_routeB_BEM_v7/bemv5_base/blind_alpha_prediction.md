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

- input path: `outputs_routeB_BEM_v7\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `e48a33fee8a70b7c035140f107513db790e891d0134354a0d1bb5988dcfd385f`
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
- `rms`: `0.0006299561639317347`
- `S_ren`: `-428.4370530555291`
- `S_ren_se`: `13.687369723891774`
- `alpha_inv_half_RT_only`: `-214.21852652776454`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-411.68189223638353`
- `alpha_inv_pred_blind_with_soft`: `-205.84094611819177`
- `a_M`: `0.03612153579144306`
- `a_M_se`: `0.0011749401185164325`
- `a_sqrtM`: `-5.409789327297648`
- `a_sqrtM_se`: `0.1731408761398122`
- `a_logM`: `74.09031086897753`
- `a_logM_se`: `2.3634658457445767`
- `b_inv_sqrt`: `1758.7722556598499`
- `b_inv_sqrt_se`: `56.66259405898382`
- `b_inv`: `-3826.257372289616`
- `b_inv_se`: `125.808247923223`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0014447255062129568`
- `S_inf`: `-0.4308327907491104`
- `S_inf_se`: `0.010953077362602637`
- `alpha_inv_pred_blind`: `-0.2154163953745552`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=639, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=639, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=639, Id=4:1:1, L=21.043322
- `5_1`: `raw_spectrum_5_1.npy`, modes=639, Id=5:1:1, L=23.598564
- `5_1_2`: `raw_spectrum_5_1_2.npy`, modes=639, Id=5:1:2, L=24.734148

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.