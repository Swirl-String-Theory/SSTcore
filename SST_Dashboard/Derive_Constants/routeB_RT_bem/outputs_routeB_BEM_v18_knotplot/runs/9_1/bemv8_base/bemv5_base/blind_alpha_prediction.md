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

- input path: `outputs_routeB_BEM_v18_knotplot\runs\9_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `b8ae018dcfb23769d44550bb7d4449c376db5697381fc34c82f2bab547e44325`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `9_1`
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
- `rms`: `0.01636036272206585`
- `S_ren`: `9589.564499235139`
- `S_ren_se`: `495.94382496406877`
- `alpha_inv_half_RT_only`: `4794.7822496175695`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `9606.319660054285`
- `alpha_inv_pred_blind_with_soft`: `4803.159830027143`
- `a_M`: `-3.6052518162878187`
- `a_M_se`: `0.1558971092351045`
- `a_sqrtM`: `285.6445184955199`
- `a_sqrtM_se`: `13.32429881955092`
- `a_logM`: `-2102.9776299382665`
- `a_logM_se`: `105.48347960672972`
- `b_inv_sqrt`: `-27295.531769892626`
- `b_inv_sqrt_se`: `1466.522535437914`
- `b_inv`: `32927.60887512242`
- `b_inv_se`: `1888.099178130926`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.08257070308908479`
- `S_inf`: `-16.31638701950542`
- `S_inf_se`: `1.0767517494452425`
- `alpha_inv_pred_blind`: `-8.15819350975271`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `9_1`: `raw_spectrum_9_1.npy`, modes=215, Id=9:1:1, L=37.744167

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.