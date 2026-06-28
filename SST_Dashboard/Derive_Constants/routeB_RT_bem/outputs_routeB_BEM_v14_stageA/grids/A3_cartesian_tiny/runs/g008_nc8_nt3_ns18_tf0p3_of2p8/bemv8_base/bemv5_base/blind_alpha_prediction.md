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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g008_nc8_nt3_ns18_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `31`
- `M_min`: `11`
- `M_max`: `41`
- `rms`: `0.0019648823578692`
- `S_ren`: `140.04292277619064`
- `S_ren_se`: `110.06790964431283`
- `alpha_inv_half_RT_only`: `70.02146138809532`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `156.7980835953362`
- `alpha_inv_pred_blind_with_soft`: `78.3990417976681`
- `a_M`: `-0.3228246293312722`
- `a_M_se`: `0.27179531005445473`
- `a_sqrtM`: `12.581321620992053`
- `a_sqrtM_se`: `10.257244744045343`
- `a_logM`: `-45.13193417805497`
- `a_logM_se`: `35.872151483374424`
- `b_inv_sqrt`: `-279.74352173292255`
- `b_inv_sqrt_se`: `220.4209263759008`
- `b_inv`: `157.81138357666583`
- `b_inv_se`: `125.48148386328518`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `31`
- `M_min`: `11`
- `M_max`: `41`
- `rms`: `0.0021021155566819457`
- `S_inf`: `-0.2556906563475077`
- `S_inf_se`: `0.07029295512140345`
- `alpha_inv_pred_blind`: `-0.12784532817375385`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=41, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=41, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=41, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.