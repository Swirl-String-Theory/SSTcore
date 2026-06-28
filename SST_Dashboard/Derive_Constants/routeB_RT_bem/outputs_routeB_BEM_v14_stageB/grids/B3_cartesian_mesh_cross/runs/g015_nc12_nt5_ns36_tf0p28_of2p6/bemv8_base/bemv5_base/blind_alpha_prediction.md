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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g015_nc12_nt5_ns36_tf0p28_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `0.01658805582754755`
- `S_ren`: `11743.069834824473`
- `S_ren_se`: `624.971991324018`
- `alpha_inv_half_RT_only`: `5871.534917412237`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `11759.82499564362`
- `alpha_inv_pred_blind_with_soft`: `5879.91249782181`
- `a_M`: `-12.623470366947686`
- `a_M_se`: `0.5381769293123649`
- `a_sqrtM`: `654.9931909614306`
- `a_sqrtM_se`: `30.57588492550371`
- `a_logM`: `-3160.5278660782947`
- `a_logM_se`: `160.88371881120466`
- `b_inv_sqrt`: `-26892.529234089514`
- `b_inv_sqrt_se`: `1486.456250233322`
- `b_inv`: `21266.935443475126`
- `b_inv_se`: `1271.6422142073257`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `0.1518700177268316`
- `S_inf`: `-35.29848420542873`
- `S_inf_se`: `2.9725116102927034`
- `alpha_inv_pred_blind`: `-17.649242102714364`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=95, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=95, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=95, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.