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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g027_nc32_nt7_ns96_tf0p24_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `240`
- `M_min`: `80`
- `M_max`: `319`
- `rms`: `0.0006790848244080913`
- `S_ren`: `161.06846900611262`
- `S_ren_se`: `18.3398495432315`
- `alpha_inv_half_RT_only`: `80.53423450305631`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `177.8236298252582`
- `alpha_inv_pred_blind_with_soft`: `88.9118149126291`
- `a_M`: `-0.03568249902090437`
- `a_M_se`: `0.0035841596855628113`
- `a_sqrtM`: `3.5034568326461475`
- `a_sqrtM_se`: `0.37315398304124875`
- `a_logM`: `-32.17036927665251`
- `a_logM_se`: `3.5986383714477093`
- `b_inv_sqrt`: `-522.0498670209847`
- `b_inv_sqrt_se`: `60.94930156805345`
- `b_inv`: `785.7314448402519`
- `b_inv_se`: `95.5977201505307`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `240`
- `M_min`: `80`
- `M_max`: `319`
- `rms`: `0.0012509212845246492`
- `S_inf`: `-0.3875526675306536`
- `S_inf_se`: `0.013405735615072375`
- `alpha_inv_pred_blind`: `-0.1937763337653268`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=319, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=319, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=319, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.