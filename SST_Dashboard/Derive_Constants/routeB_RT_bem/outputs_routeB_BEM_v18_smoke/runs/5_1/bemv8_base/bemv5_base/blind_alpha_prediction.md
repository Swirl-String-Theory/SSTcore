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

- input path: `/mnt/data/outputs_routeB_BEM_v18_smoke/runs/5_1/bemv8_base/bemv5_base/idealxml_sampled_ideal_used.txt`
- input sha256: `69aec4ab23f18ef79c6621f56788fa60d67083c1b4174b1cff18bc3cf66ecd7d`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
- target: `5_1`
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
- `rms`: `0.0014192800001452787`
- `S_ren`: `153.25516533066494`
- `S_ren_se`: `89.18654854543058`
- `alpha_inv_half_RT_only`: `76.62758266533247`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `170.0103261498105`
- `alpha_inv_pred_blind_with_soft`: `85.00516307490525`
- `a_M`: `-1.121025035638496`
- `a_M_se`: `0.6414388100904476`
- `a_sqrtM`: `28.381900805631698`
- `a_sqrtM_se`: `16.426620632496988`
- `a_logM`: `-67.01191087707153`
- `a_logM_se`: `38.94527703415285`
- `b_inv_sqrt`: `-278.89514928422886`
- `b_inv_sqrt_se`: `162.05756853782347`
- `b_inv`: `107.62414567329635`
- `b_inv_se`: `62.40505856804448`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `15`
- `M_min`: `5`
- `M_max`: `19`
- `rms`: `0.001728471650185374`
- `S_inf`: `-0.4695636592092157`
- `S_inf_se`: `0.08036947928599765`
- `alpha_inv_pred_blind`: `-0.23478182960460786`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=19, Id=0:1:1, L=6.283185307179586
- `5_1`: `raw_spectrum_5_1.npy`, modes=19, Id=5:1:1, L=23.598564

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.