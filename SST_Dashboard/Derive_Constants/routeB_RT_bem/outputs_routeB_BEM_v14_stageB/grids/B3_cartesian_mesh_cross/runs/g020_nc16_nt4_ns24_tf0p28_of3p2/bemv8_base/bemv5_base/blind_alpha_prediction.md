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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g020_nc16_nt4_ns24_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `66`
- `M_min`: `22`
- `M_max`: `87`
- `rms`: `0.001077114411033476`
- `S_ren`: `239.891732399775`
- `S_ren_se`: `41.47833733936517`
- `alpha_inv_half_RT_only`: `119.9458661998875`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `256.6468932189206`
- `alpha_inv_pred_blind_with_soft`: `128.3234466094603`
- `a_M`: `-0.24365035153481251`
- `a_M_se`: `0.03990425673139109`
- `a_sqrtM`: `12.91007273800375`
- `a_sqrtM_se`: `2.169619945172289`
- `a_logM`: `-63.755926345403104`
- `a_logM_se`: `10.924937467813818`
- `b_inv_sqrt`: `-556.0210781263504`
- `b_inv_sqrt_se`: `96.59452456579487`
- `b_inv`: `452.02574393661786`
- `b_inv_se`: `79.07691787103258`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `66`
- `M_min`: `22`
- `M_max`: `87`
- `rms`: `0.0016204731336521751`
- `S_inf`: `-0.43972765424450666`
- `S_inf_se`: `0.03313933428277925`
- `alpha_inv_pred_blind`: `-0.21986382712225333`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=87, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=87, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=87, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.