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

- input path: `/mnt/data/outputs_routeB_BEM_v18_smoke/runs/3_1/bemv8_base/bemv5_base/idealxml_sampled_ideal_used.txt`
- input sha256: `57871a0d4616a5802758c431cd855bb659f72a1914ff256ccbd47d134d87daaa`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
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
- `n_points`: `15`
- `M_min`: `5`
- `M_max`: `19`
- `rms`: `0.0008008164169719602`
- `S_ren`: `-130.71260556476872`
- `S_ren_se`: `50.322735641266476`
- `alpha_inv_half_RT_only`: `-65.35630278238436`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-113.95744474562316`
- `alpha_inv_pred_blind_with_soft`: `-56.97872237281158`
- `a_M`: `0.9059130138387701`
- `a_M_se`: `0.36192627920551945`
- `a_sqrtM`: `-23.815885747392628`
- `a_sqrtM_se`: `9.26857806530592`
- `a_logM`: `57.0106776232031`
- `a_logM_se`: `21.974534418351716`
- `b_inv_sqrt`: `236.3233818326558`
- `b_inv_sqrt_se`: `91.43957595848842`
- `b_inv`: `-89.74213053368443`
- `b_inv_se`: `35.21151245580239`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `15`
- `M_min`: `5`
- `M_max`: `19`
- `rms`: `0.0014886042159164186`
- `S_inf`: `-0.6081925008902215`
- `S_inf_se`: `0.06921626147776996`
- `alpha_inv_pred_blind`: `-0.30409625044511074`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=19, Id=0:1:1, L=6.283185307179586
- `3_1`: `raw_spectrum_3_1.npy`, modes=19, Id=3:1:1, L=16.371637

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.