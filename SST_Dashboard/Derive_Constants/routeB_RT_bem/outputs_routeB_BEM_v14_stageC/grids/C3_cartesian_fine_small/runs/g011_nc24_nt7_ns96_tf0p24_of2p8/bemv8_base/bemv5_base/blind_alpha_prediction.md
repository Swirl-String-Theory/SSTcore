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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g011_nc24_nt7_ns96_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0018333360362003401`
- `S_ren`: `851.138638008358`
- `S_ren_se`: `52.43638789252322`
- `alpha_inv_half_RT_only`: `425.569319004179`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `867.8937988275036`
- `alpha_inv_pred_blind_with_soft`: `433.9468994137518`
- `a_M`: `-0.24759346796768167`
- `a_M_se`: `0.01291993047246124`
- `a_sqrtM`: `21.784779279269745`
- `a_sqrtM_se`: `1.2213340716463383`
- `a_logM`: `-178.3460575074527`
- `a_logM_se`: `10.694270477001096`
- `b_inv_sqrt`: `-2574.352739856601`
- `b_inv_sqrt_se`: `164.45269869635604`
- `b_inv`: `3453.7007826816293`
- `b_inv_se`: `234.19182804786126`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.006827415979257376`
- `S_inf`: `-1.6889491577517914`
- `S_inf_se`: `0.08054304326160337`
- `alpha_inv_pred_blind`: `-0.8444745788758957`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=263, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=263, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=263, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.