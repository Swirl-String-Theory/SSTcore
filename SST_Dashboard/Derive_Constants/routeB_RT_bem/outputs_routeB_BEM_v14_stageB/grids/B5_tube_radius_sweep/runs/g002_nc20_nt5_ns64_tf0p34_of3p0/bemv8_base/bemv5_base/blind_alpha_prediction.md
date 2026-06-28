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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B5_tube_radius_sweep\runs\g002_nc20_nt5_ns64_tf0p34_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0008700425270663289`
- `S_ren`: `66.3141370333113`
- `S_ren_se`: `28.480364121707126`
- `alpha_inv_half_RT_only`: `33.15706851665565`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `83.06929785245686`
- `alpha_inv_pred_blind_with_soft`: `41.53464892622843`
- `a_M`: `-0.037942979826082746`
- `a_M_se`: `0.012549003546135973`
- `a_sqrtM`: `2.5330071529247333`
- `a_sqrtM_se`: `0.9338553593441522`
- `a_logM`: `-15.730597260455136`
- `a_logM_se`: `6.436789584290728`
- `b_inv_sqrt`: `-171.30392868128047`
- `b_inv_sqrt_se`: `77.91268489018468`
- `b_inv`: `172.2918602560823`
- `b_inv_se`: `87.32998511101984`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `123`
- `M_min`: `41`
- `M_max`: `163`
- `rms`: `0.0012568715973816868`
- `S_inf`: `-0.31166417296796123`
- `S_inf_se`: `0.018808058440838587`
- `alpha_inv_pred_blind`: `-0.15583208648398061`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=163, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=163, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=163, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.