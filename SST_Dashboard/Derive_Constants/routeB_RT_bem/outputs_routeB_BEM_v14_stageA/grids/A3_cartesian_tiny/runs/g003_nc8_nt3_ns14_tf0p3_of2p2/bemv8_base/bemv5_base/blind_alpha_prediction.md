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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g003_nc8_nt3_ns14_tf0p3_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.002276496333612307`
- `S_ren`: `-277.4836066536433`
- `S_ren_se`: `133.9210910891091`
- `alpha_inv_half_RT_only`: `-138.74180332682164`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-260.72844583449773`
- `alpha_inv_pred_blind_with_soft`: `-130.36422291724887`
- `a_M`: `0.7785251838202338`
- `a_M_se`: `0.3776470626263603`
- `a_sqrtM`: `-28.002251395285988`
- `a_sqrtM_se`: `13.558218350535258`
- `a_logM`: `93.27735381773613`
- `a_logM_se`: `45.11083819840291`
- `b_inv_sqrt`: `548.8216359534821`
- `b_inv_sqrt_se`: `263.72489013477457`
- `b_inv`: `-300.7533391188654`
- `b_inv_se`: `142.84818954647145`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0024862311158531793`
- `S_inf`: `-0.4603155490650084`
- `S_inf_se`: `0.08879443160463471`
- `alpha_inv_pred_blind`: `-0.2301577745325042`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=37, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=37, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=37, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.