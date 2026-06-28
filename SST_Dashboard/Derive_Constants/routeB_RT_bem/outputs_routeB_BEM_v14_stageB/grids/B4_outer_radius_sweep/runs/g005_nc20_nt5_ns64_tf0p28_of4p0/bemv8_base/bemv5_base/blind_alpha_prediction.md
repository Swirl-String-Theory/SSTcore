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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B4_outer_radius_sweep\runs\g005_nc20_nt5_ns64_tf0p28_of4p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0005379322500049387`
- `S_ren`: `108.72555160965543`
- `S_ren_se`: `17.608916663658515`
- `alpha_inv_half_RT_only`: `54.36277580482771`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `125.48071242880098`
- `alpha_inv_pred_blind_with_soft`: `62.74035621440049`
- `a_M`: `-0.05184791177593073`
- `a_M_se`: `0.007758831899464431`
- `a_sqrtM`: `3.718055190233385`
- `a_sqrtM_se`: `0.5773866207724728`
- `a_logM`: `-24.878472975891725`
- `a_logM_se`: `3.9797556971854693`
- `b_inv_sqrt`: `-293.7909270248524`
- `b_inv_sqrt_se`: `48.17206582788985`
- `b_inv`: `322.89863111943913`
- `b_inv_se`: `53.99461971367211`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.0007844921074401402`
- `S_inf`: `-0.23477230572738636`
- `S_inf_se`: `0.01173928461256337`
- `alpha_inv_pred_blind`: `-0.11738615286369318`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=163, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=163, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=163, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.