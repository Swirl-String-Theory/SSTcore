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

- input path: `outputs_routeB_BEM_v10\runs\g004_nc48_nt8_ns256_tf0p2_of3p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0005939956655632798`
- `S_ren`: `-78.45497343991524`
- `S_ren_se`: `12.906038157021372`
- `alpha_inv_half_RT_only`: `-39.22748671995762`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-61.69981262076968`
- `alpha_inv_pred_blind_with_soft`: `-30.84990631038484`
- `a_M`: `0.007666451123306411`
- `a_M_se`: `0.0011078696862640686`
- `a_sqrtM`: `-1.096872055139767`
- `a_sqrtM_se`: `0.16325728018437477`
- `a_logM`: `13.988043157186482`
- `a_logM_se`: `2.228549458611635`
- `b_inv_sqrt`: `300.0875800633926`
- `b_inv_sqrt_se`: `53.42805928041577`
- `b_inv`: `-570.9748076111186`
- `b_inv_se`: `118.62659378090163`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `480`
- `M_min`: `160`
- `M_max`: `639`
- `rms`: `0.0006496394720701014`
- `S_inf`: `-0.30327559078181854`
- `S_inf_se`: `0.0049251926160257765`
- `alpha_inv_pred_blind`: `-0.15163779539090927`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=639, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=639, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=639, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.