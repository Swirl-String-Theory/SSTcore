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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g029_nc16_nt5_ns36_tf0p32_of2p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `87`
- `M_min`: `29`
- `M_max`: `115`
- `rms`: `0.001426621675984585`
- `S_ren`: `-145.75912259063236`
- `S_ren_se`: `51.21112495285188`
- `alpha_inv_half_RT_only`: `-72.87956129531618`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-129.0039617714868`
- `alpha_inv_pred_blind_with_soft`: `-64.5019808857434`
- `a_M`: `0.06444578425788361`
- `a_M_se`: `0.0347228539777319`
- `a_sqrtM`: `-4.962551954061312`
- `a_sqrtM_se`: `2.1704095389145177`
- `a_logM`: `33.519764274713694`
- `a_logM_se`: `12.565022077187761`
- `b_inv_sqrt`: `385.3782134199297`
- `b_inv_sqrt_se`: `127.73468471914217`
- `b_inv`: `-400.7075908365344`
- `b_inv_se`: `120.23886898033639`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `87`
- `M_min`: `29`
- `M_max`: `115`
- `rms`: `0.002723119690499984`
- `S_inf`: `-0.6374779225611011`
- `S_inf_se`: `0.04846360945112169`
- `alpha_inv_pred_blind`: `-0.31873896128055057`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=115, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=115, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=115, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.