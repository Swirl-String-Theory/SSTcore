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

- input path: `outputs_routeB_BEM_v18_production\runs\6_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `7fc576f6b09b6cca89767568da58b7a734a20f556023a949229586ff8ea78dfb`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `6_1`
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
- `rms`: `0.0016651193941045405`
- `S_ren`: `240.29899040563654`
- `S_ren_se`: `50.47600076862982`
- `alpha_inv_half_RT_only`: `120.14949520281827`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `257.0541512247821`
- `alpha_inv_pred_blind_with_soft`: `128.52707561239106`
- `a_M`: `-0.10080976596495872`
- `a_M_se`: `0.015866842592804572`
- `a_sqrtM`: `7.620521379321549`
- `a_sqrtM_se`: `1.356115922011596`
- `a_logM`: `-53.70989024927632`
- `a_logM_se`: `10.735861461916155`
- `b_inv_sqrt`: `-667.949618345386`
- `b_inv_sqrt_se`: `149.2592283638982`
- `b_inv`: `772.4802297582364`
- `b_inv_se`: `192.1663115242754`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.003981216871281054`
- `S_inf`: `-1.18620456271155`
- `S_inf_se`: `0.051916503925706174`
- `alpha_inv_pred_blind`: `-0.593102281355775`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `6_1`: `raw_spectrum_6_1.npy`, modes=215, Id=6:1:1, L=28.354929

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.