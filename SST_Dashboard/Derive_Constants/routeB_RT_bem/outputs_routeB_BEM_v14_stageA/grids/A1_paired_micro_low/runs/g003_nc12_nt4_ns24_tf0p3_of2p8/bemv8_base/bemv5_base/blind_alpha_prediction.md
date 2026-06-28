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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A1_paired_micro_low\runs\g003_nc12_nt4_ns24_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.002481284562644603`
- `S_ren`: `455.63354467053506`
- `S_ren_se`: `100.43689473784839`
- `alpha_inv_half_RT_only`: `227.81677233526753`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `472.3887054896806`
- `alpha_inv_pred_blind_with_soft`: `236.1943527448403`
- `a_M`: `-0.7276801572299956`
- `a_M_se`: `0.12506912788675004`
- `a_sqrtM`: `32.46175971347283`
- `a_sqrtM_se`: `6.1437629683316635`
- `a_logM`: `-134.0713056045187`
- `a_logM_se`: `27.9491487303931`
- `b_inv_sqrt`: `-971.251844737889`
- `b_inv_sqrt_se`: `223.24337228669427`
- `b_inv`: `651.4909372585126`
- `b_inv_se`: `165.0930222702744`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0070902270999669585`
- `S_inf`: `-1.3405951780909624`
- `S_inf_se`: `0.1605128751494099`
- `alpha_inv_pred_blind`: `-0.6702975890454812`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.