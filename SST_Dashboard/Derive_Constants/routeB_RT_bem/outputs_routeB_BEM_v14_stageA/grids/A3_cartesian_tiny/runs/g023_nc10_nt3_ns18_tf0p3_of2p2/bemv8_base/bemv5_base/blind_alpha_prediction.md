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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g023_nc10_nt3_ns18_tf0p3_of2p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.001986687444051918`
- `S_ren`: `-339.5794203827297`
- `S_ren_se`: `89.03438875173802`
- `alpha_inv_half_RT_only`: `-169.78971019136486`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-322.8242595635842`
- `alpha_inv_pred_blind_with_soft`: `-161.4121297817921`
- `a_M`: `0.7362282592459941`
- `a_M_se`: `0.18894153864756177`
- `a_sqrtM`: `-29.225011383486994`
- `a_sqrtM_se`: `7.556051442391935`
- `a_logM`: `107.26640108187198`
- `a_logM_se`: `27.980919247954414`
- `b_inv_sqrt`: `693.1559869444691`
- `b_inv_sqrt_se`: `181.90742904912307`
- `b_inv`: `-415.89505216036616`
- `b_inv_se`: `109.47641025083698`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0024537201760475007`
- `S_inf`: `-0.412903339898576`
- `S_inf_se`: `0.06846790730811557`
- `alpha_inv_pred_blind`: `-0.206451669949288`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.