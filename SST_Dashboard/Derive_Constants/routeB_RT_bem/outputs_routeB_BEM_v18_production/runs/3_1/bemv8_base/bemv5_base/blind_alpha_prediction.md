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

- input path: `outputs_routeB_BEM_v18_production\runs\3_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `d18e1dfd7fdba9a3323d0f1df8c057cb7a20b13a70fb2af143e4520f29c33d03`
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
- `rms`: `0.0007727860295395441`
- `S_ren`: `43.6640994865639`
- `S_ren_se`: `23.42603681101287`
- `alpha_inv_half_RT_only`: `21.83204974328195`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `60.41926030570946`
- `alpha_inv_pred_blind_with_soft`: `30.20963015285473`
- `a_M`: `-0.01657210768430084`
- `a_M_se`: `0.007363840894554226`
- `a_sqrtM`: `1.2805871233110784`
- `a_sqrtM_se`: `0.6293767538094652`
- `a_logM`: `-9.485910926516706`
- `a_logM_se`: `4.982539860033553`
- `b_inv_sqrt`: `-127.47610809138358`
- `b_inv_sqrt_se`: `69.27157708201634`
- `b_inv`: `163.18691948349814`
- `b_inv_se`: `89.18486050903597`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0009956717939551662`
- `S_inf`: `-0.35116781302822686`
- `S_inf_se`: `0.012983919306801086`
- `alpha_inv_pred_blind`: `-0.17558390651411343`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.