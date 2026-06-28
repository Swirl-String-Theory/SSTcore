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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C2_paired_fine_alt_tail\runs\g001_nc24_nt5_ns96_tf0p34_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0008924636326164055`
- `S_ren`: `184.4827889447089`
- `S_ren_se`: `27.05391286980086`
- `alpha_inv_half_RT_only`: `92.24139447235444`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `201.23794976385446`
- `alpha_inv_pred_blind_with_soft`: `100.61897488192723`
- `a_M`: `-0.06315219598869048`
- `a_M_se`: `0.008504243016244657`
- `a_sqrtM`: `5.184621762169259`
- `a_sqrtM_se`: `0.7268452618427854`
- `a_logM`: `-39.734493199789746`
- `a_logM_se`: `5.754161505470173`
- `b_inv_sqrt`: `-537.7732092401806`
- `b_inv_sqrt_se`: `79.99932834774432`
- `b_inv`: `676.3421467627904`
- `b_inv_se`: `102.99648485067333`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0013134943732536996`
- `S_inf`: `-0.36881161810162355`
- `S_inf_se`: `0.017128440371417447`
- `alpha_inv_pred_blind`: `-0.18440580905081178`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.