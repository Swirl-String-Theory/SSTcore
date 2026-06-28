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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g028_nc10_nt4_ns14_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `40`
- `M_min`: `14`
- `M_max`: `53`
- `rms`: `0.01844350816474856`
- `S_ren`: `13911.113818875114`
- `S_ren_se`: `926.7233731259153`
- `alpha_inv_half_RT_only`: `6955.556909437557`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `13927.86897969426`
- `alpha_inv_pred_blind_with_soft`: `6963.93448984713`
- `a_M`: `-28.600519584136805`
- `a_M_se`: `1.6460501929555864`
- `a_sqrtM`: `1155.1535330943732`
- `a_sqrtM_se`: `70.4279553180124`
- `a_logM`: `-4333.377185013594`
- `a_logM_se`: `279.21529475449194`
- `b_inv_sqrt`: `-28618.575105490065`
- `b_inv_sqrt_se`: `1944.7201768247553`
- `b_inv`: `17536.79616345056`
- `b_inv_se`: `1254.76926398107`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `40`
- `M_min`: `14`
- `M_max`: `53`
- `rms`: `0.11999024251799256`
- `S_inf`: `-24.14413506521385`
- `S_inf_se`: `3.4291474326032114`
- `alpha_inv_pred_blind`: `-12.072067532606924`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=53, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=53, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=53, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.