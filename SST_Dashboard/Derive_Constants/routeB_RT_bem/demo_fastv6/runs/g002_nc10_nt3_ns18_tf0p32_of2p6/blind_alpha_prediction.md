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

- input path: `/mnt/data/outputs_routeB_BEM_v6_fast/runs/g002_nc10_nt3_ns18_tf0p32_of2p6/idealxml_sampled_ideal_used.txt`
- input sha256: `f05c65f845f5e00742e92da382adbfe5b1095401368ce8776282a1966a5a2a21`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
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
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0020272594050106054`
- `S_ren`: `-178.48061499226026`
- `S_ren_se`: `90.85301262258561`
- `alpha_inv_half_RT_only`: `-89.24030749613013`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-161.72545417311468`
- `alpha_inv_pred_blind_with_soft`: `-80.86272708655734`
- `a_M`: `0.37489917413802054`
- `a_M_se`: `0.19280086928420898`
- `a_sqrtM`: `-15.011264704236613`
- `a_sqrtM_se`: `7.710391916969856`
- `a_logM`: `55.81739809498872`
- `a_logM_se`: `28.55245984224167`
- `b_inv_sqrt`: `367.4803214387469`
- `b_inv_sqrt_se`: `185.62308507309217`
- `b_inv`: `-225.61541826540105`
- `b_inv_se`: `111.7125830547679`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0021481395149739175`
- `S_inf`: `-0.14236202431550848`
- `S_inf_se`: `0.05994107177931778`
- `alpha_inv_pred_blind`: `-0.07118101215775424`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185307179586
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.