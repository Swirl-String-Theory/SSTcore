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

- input path: `outputs_routeB_BEM_v18_production\runs\5_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `ac795d665b90aceb78b01e29700e4215923160f4abfe87e3ceef51f3a62a17a4`
- source: `XML/Fourier ideal.txt=ideal.txt`
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
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.001025153531489653`
- `S_ren`: `171.3057656383371`
- `S_ren_se`: `31.076240314444725`
- `alpha_inv_half_RT_only`: `85.65288281916855`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `188.06092645748268`
- `alpha_inv_pred_blind_with_soft`: `94.03046322874134`
- `a_M`: `-0.0625824911046795`
- `a_M_se`: `0.009768638678520387`
- `a_sqrtM`: `5.002074143201269`
- `a_sqrtM_se`: `0.8349113171594301`
- `a_logM`: `-37.33376619484439`
- `a_logM_se`: `6.609679960628719`
- `b_inv_sqrt`: `-491.4931049603622`
- `b_inv_sqrt_se`: `91.89348560014683`
- `b_inv`: `601.2696460273246`
- `b_inv_se`: `118.3098182568424`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.001697618494644699`
- `S_inf`: `-0.5302028361620157`
- `S_inf_se`: `0.022137557458208376`
- `alpha_inv_pred_blind`: `-0.26510141808100784`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `5_1`: `raw_spectrum_5_1.npy`, modes=215, Id=5:1:1, L=23.598564

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.