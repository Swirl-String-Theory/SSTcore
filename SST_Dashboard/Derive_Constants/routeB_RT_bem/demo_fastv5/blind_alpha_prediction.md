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

- input path: `/mnt/data/outputs_routeB_BEM_v5_fast/idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0021451955956130076`
- `S_ren`: `-183.93247043925572`
- `S_ren_se`: `96.13840342505355`
- `alpha_inv_half_RT_only`: `-91.96623521962786`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-167.17730962011015`
- `alpha_inv_pred_blind_with_soft`: `-83.58865481005508`
- `a_M`: `0.3799493571517987`
- `a_M_se`: `0.204017095491872`
- `a_sqrtM`: `-15.318270779563685`
- `a_sqrtM_se`: `8.158945391918081`
- `a_logM`: `57.3135705742606`
- `a_logM_se`: `30.213504471162473`
- `b_inv_sqrt`: `379.3689119803287`
- `b_inv_sqrt_se`: `196.42174235754143`
- `b_inv`: `-233.95707160516014`
- `b_inv_se`: `118.21148322278309`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0022629075359335516`
- `S_inf`: `-0.16776969212666007`
- `S_inf_se`: `0.06314352587243344`
- `alpha_inv_pred_blind`: `-0.08388484606333003`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185307179586
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.