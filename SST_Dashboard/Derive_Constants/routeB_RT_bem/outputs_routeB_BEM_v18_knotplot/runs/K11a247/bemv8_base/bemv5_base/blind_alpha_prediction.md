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

- input path: `outputs_routeB_BEM_v18_knotplot\runs\K11a247\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `9ca849c18194f9927cd29ac530b7b2e79d68f19a49c6754edfc223bbea3cc027`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `K11a247`
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
- `rms`: `0.01131316046935297`
- `S_ren`: `7033.4520936641`
- `S_ren_se`: `342.94423485097036`
- `alpha_inv_half_RT_only`: `3516.72604683205`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `7050.207254483245`
- `alpha_inv_pred_blind_with_soft`: `3525.1036272416227`
- `a_M`: `-2.7065735342246953`
- `a_M_se`: `0.10780256180422156`
- `a_sqrtM`: `212.33849464122804`
- `a_sqrtM_se`: `9.213727913494314`
- `a_logM`: `-1548.599527198176`
- `a_logM_se`: `72.94163044729662`
- `b_inv_sqrt`: `-19925.561885876064`
- `b_inv_sqrt_se`: `1014.0976124541894`
- `b_inv`: `23846.15259967146`
- `b_inv_se`: `1305.6170787362237`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.06884329667639136`
- `S_inf`: `-14.481260465062944`
- `S_inf_se`: `0.8977414186955285`
- `alpha_inv_pred_blind`: `-7.240630232531472`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `K11a247`: `raw_spectrum_K11a247.npy`, modes=215, Id=K11a247, L=46.146275

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.