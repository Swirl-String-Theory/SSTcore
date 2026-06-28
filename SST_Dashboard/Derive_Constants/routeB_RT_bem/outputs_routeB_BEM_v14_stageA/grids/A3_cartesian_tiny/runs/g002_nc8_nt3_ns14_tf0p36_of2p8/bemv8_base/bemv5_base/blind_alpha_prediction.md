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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g002_nc8_nt3_ns14_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0015357182509291246`
- `S_ren`: `-180.6124125375043`
- `S_ren_se`: `90.34280474484257`
- `alpha_inv_half_RT_only`: `-90.30620626875215`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-163.85725171835873`
- `alpha_inv_pred_blind_with_soft`: `-81.92862585917936`
- `a_M`: `0.5036944342288754`
- `a_M_se`: `0.25475968395908`
- `a_sqrtM`: `-18.098259411661118`
- `a_sqrtM_se`: `9.146337318259498`
- `a_logM`: `60.49295061214024`
- `a_logM_se`: `30.431649071039622`
- `b_inv_sqrt`: `358.40356142610176`
- `b_inv_sqrt_se`: `177.90809544665197`
- `b_inv`: `-198.1934164463717`
- `b_inv_se`: `96.36500114656423`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `28`
- `M_min`: `10`
- `M_max`: `37`
- `rms`: `0.0016639012025731102`
- `S_inf`: `-0.09283597855535546`
- `S_inf_se`: `0.05942535293145786`
- `alpha_inv_pred_blind`: `-0.04641798927767773`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=37, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=37, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=37, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.