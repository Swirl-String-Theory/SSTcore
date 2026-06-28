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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g017_nc10_nt3_ns14_tf0p36_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.0019281880550687447`
- `S_ren`: `-362.2374918213749`
- `S_ren_se`: `88.4316464097874`
- `alpha_inv_half_RT_only`: `-181.11874591068744`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-345.48233100222933`
- `alpha_inv_pred_blind_with_soft`: `-172.74116550111466`
- `a_M`: `0.9141759727156238`
- `a_M_se`: `0.21089465070484706`
- `a_sqrtM`: `-34.26054556309657`
- `a_sqrtM_se`: `8.06904603616392`
- `a_logM`: `118.74881524898444`
- `a_logM_se`: `28.58687844234827`
- `b_inv_sqrt`: `723.9101431614799`
- `b_inv_sqrt_se`: `177.7950403189252`
- `b_inv`: `-409.15621215477273`
- `b_inv_se`: `102.3622542955986`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `33`
- `M_min`: `11`
- `M_max`: `43`
- `rms`: `0.002686840335292423`
- `S_inf`: `-0.27560858530544047`
- `S_inf_se`: `0.0784984614454793`
- `alpha_inv_pred_blind`: `-0.13780429265272023`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=43, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=43, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=43, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.