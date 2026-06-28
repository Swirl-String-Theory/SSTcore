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

- input path: `/mnt/data/outputs_routeB_BEM_v18_smoke/runs/4_1/bemv8_base/bemv5_base/idealxml_sampled_ideal_used.txt`
- input sha256: `b6f046d30f5130be5cc607fb8d43483ada3062c667c155b23a4bb56c9b024cce`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
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
- `n_points`: `15`
- `M_min`: `5`
- `M_max`: `19`
- `rms`: `0.32135390355867455`
- `S_ren`: `45868.58582558637`
- `S_ren_se`: `20193.651370459418`
- `alpha_inv_half_RT_only`: `22934.292912793186`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `45885.340986405514`
- `alpha_inv_pred_blind_with_soft`: `22942.670493202757`
- `a_M`: `-366.5373250413977`
- `a_M_se`: `145.23481307106218`
- `a_sqrtM`: `9045.612942665377`
- `a_sqrtM_se`: `3719.321530628229`
- `a_logM`: `-20682.839424919428`
- `a_logM_se`: `8818.004057562955`
- `b_inv_sqrt`: `-83083.8948164195`
- `b_inv_sqrt_se`: `36693.13472008785`
- `b_inv`: `30921.699242991006`
- `b_inv_se`: `14129.776485680097`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `15`
- `M_min`: `5`
- `M_max`: `19`
- `rms`: `0.5349518418484592`
- `S_inf`: `-46.5806799611245`
- `S_inf_se`: `24.873882639518598`
- `alpha_inv_pred_blind`: `-23.29033998056225`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=19, Id=0:1:1, L=6.283185307179586
- `4_1`: `raw_spectrum_4_1.npy`, modes=19, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.