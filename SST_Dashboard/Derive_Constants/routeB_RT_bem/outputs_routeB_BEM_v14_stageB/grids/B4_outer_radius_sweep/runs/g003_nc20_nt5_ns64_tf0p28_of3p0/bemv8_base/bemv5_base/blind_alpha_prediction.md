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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B4_outer_radius_sweep\runs\g003_nc20_nt5_ns64_tf0p28_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.000879515919366899`
- `S_ren`: `60.35781113033373`
- `S_ren_se`: `28.790470413979712`
- `alpha_inv_half_RT_only`: `30.178905565166865`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `77.11297194947929`
- `alpha_inv_pred_blind_with_soft`: `38.556485974739644`
- `a_M`: `-0.036467288914548535`
- `a_M_se`: `0.012685642422829328`
- `a_sqrtM`: `2.3800902098821557`
- `a_sqrtM_se`: `0.9440235728461832`
- `a_logM`: `-14.465383799219987`
- `a_logM_se`: `6.506876081204643`
- `b_inv_sqrt`: `-154.14563887968097`
- `b_inv_sqrt_se`: `78.76103127118768`
- `b_inv`: `151.55550875577413`
- `b_inv_se`: `88.28087105374406`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.0013721649741279315`
- `S_inf`: `-0.39339109347376683`
- `S_inf_se`: `0.02053332979886934`
- `alpha_inv_pred_blind`: `-0.19669554673688341`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=163, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=163, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=163, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.