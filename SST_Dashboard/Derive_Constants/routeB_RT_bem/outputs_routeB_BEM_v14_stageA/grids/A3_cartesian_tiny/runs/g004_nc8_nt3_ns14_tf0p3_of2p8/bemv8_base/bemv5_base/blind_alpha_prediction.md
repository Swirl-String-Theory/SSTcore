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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g004_nc8_nt3_ns14_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0017512444261226032`
- `S_ren`: `-203.3759214159923`
- `S_ren_se`: `103.02171843954332`
- `alpha_inv_half_RT_only`: `-101.68796070799615`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-186.62076059684674`
- `alpha_inv_pred_blind_with_soft`: `-93.31038029842337`
- `a_M`: `0.5436318863727987`
- `a_M_se`: `0.29051323461459927`
- `a_sqrtM`: `-19.88581355599058`
- `a_sqrtM_se`: `10.429954998808133`
- `a_logM`: `67.49244910231732`
- `a_logM_se`: `34.7024955789477`
- `b_inv_sqrt`: `404.8081973453824`
- `b_inv_sqrt_se`: `202.87612022878557`
- `b_inv`: `-225.93638947342993`
- `b_inv_se`: `109.88908351458232`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0019097055037831324`
- `S_inf`: `-0.1907069743807435`
- `S_inf_se`: `0.06820412376766329`
- `alpha_inv_pred_blind`: `-0.09535348719037175`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=37, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=37, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=37, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.