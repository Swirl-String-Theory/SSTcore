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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g006_nc8_nt3_ns18_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `31`
- `M_min`: `11`
- `M_max`: `41`
- `rms`: `0.0017129803926320953`
- `S_ren`: `114.61019390264124`
- `S_ren_se`: `95.95697692719584`
- `alpha_inv_half_RT_only`: `57.30509695132062`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `131.36535472178682`
- `alpha_inv_pred_blind_with_soft`: `65.68267736089341`
- `a_M`: `-0.23667420929433636`
- `a_M_se`: `0.23695059150387826`
- `a_sqrtM`: `9.678677837859684`
- `a_sqrtM_se`: `8.942244841585541`
- `a_logM`: `-36.1200892445612`
- `a_logM_se`: `31.27326777934217`
- `b_inv_sqrt`: `-230.96698553454092`
- `b_inv_sqrt_se`: `192.16250962585903`
- `b_inv`: `133.56723200582886`
- `b_inv_se`: `109.39449918481938`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `31`
- `M_min`: `11`
- `M_max`: `41`
- `rms`: `0.0020240863021386084`
- `S_inf`: `-0.17281708414229038`
- `S_inf_se`: `0.06768372325955997`
- `alpha_inv_pred_blind`: `-0.08640854207114519`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=41, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=41, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=41, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.