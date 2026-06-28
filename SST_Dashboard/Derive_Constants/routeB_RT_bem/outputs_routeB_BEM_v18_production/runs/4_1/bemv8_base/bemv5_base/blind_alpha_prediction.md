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

- input path: `outputs_routeB_BEM_v18_production\runs\4_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `214c25112891535bcfa39dfc00192dffa42a39d758f7fd7de0bc0c5205f98ac7`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `4_1`
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
- `rms`: `0.0010215691429056508`
- `S_ren`: `-91.8710137955097`
- `S_ren_se`: `30.96758408140718`
- `alpha_inv_half_RT_only`: `-45.93550689775485`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-75.11585297636414`
- `alpha_inv_pred_blind_with_soft`: `-37.55792648818207`
- `a_M`: `0.017818008641780292`
- `a_M_se`: `0.009734483212158534`
- `a_sqrtM`: `-1.9889253569361498`
- `a_sqrtM_se`: `0.8319920992062599`
- `a_logM`: `18.53580680663632`
- `a_logM_se`: `6.5865696062602765`
- `b_inv_sqrt`: `285.5912880762133`
- `b_inv_sqrt_se`: `91.5721854723009`
- `b_inv`: `-391.79882835544777`
- `b_inv_se`: `117.8961549869915`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.002082357533454907`
- `S_inf`: `-0.6733046686803884`
- `S_inf_se`: `0.02715469328993094`
- `alpha_inv_pred_blind`: `-0.3366523343401942`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.