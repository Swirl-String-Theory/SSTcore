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

- input path: `outputs_routeB_BEM_v18_knotplot\runs\K11a367\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `12a8654824d245331d74e42aee2ef21ec7e29577cc39ebb00a162c2943d07bfe`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `K11a367`
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
- `rms`: `0.012029932822520538`
- `S_ren`: `7717.494252163646`
- `S_ren_se`: `364.67228749243`
- `alpha_inv_half_RT_only`: `3858.747126081823`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `7734.249412982791`
- `alpha_inv_pred_blind_with_soft`: `3867.1247064913955`
- `a_M`: `-2.9523256158627618`
- `a_M_se`: `0.11463265107160407`
- `a_sqrtM`: `232.1662211216419`
- `a_sqrtM_se`: `9.797485693284624`
- `a_logM`: `-1697.3663914220751`
- `a_logM_se`: `77.56302198869831`
- `b_inv_sqrt`: `-21893.414014115857`
- `b_inv_sqrt_se`: `1078.3481933585697`
- `b_inv`: `26264.260028449247`
- `b_inv_se`: `1388.3375730133678`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.07333661201322365`
- `S_inf`: `-15.470007448464997`
- `S_inf_se`: `0.9563358713129835`
- `alpha_inv_pred_blind`: `-7.735003724232499`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `K11a367`: `raw_spectrum_K11a367.npy`, modes=215, Id=K11a367, L=44.804989

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.