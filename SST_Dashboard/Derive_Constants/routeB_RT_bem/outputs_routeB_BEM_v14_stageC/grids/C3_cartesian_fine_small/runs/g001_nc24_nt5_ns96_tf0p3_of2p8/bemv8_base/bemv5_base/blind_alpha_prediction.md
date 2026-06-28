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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g001_nc24_nt5_ns96_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.000813591555984292`
- `S_ren`: `115.27659991068404`
- `S_ren_se`: `24.663005037724982`
- `alpha_inv_half_RT_only`: `57.63829995534202`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `132.0317607298296`
- `alpha_inv_pred_blind_with_soft`: `66.0158803649148`
- `a_M`: `-0.03867618720349042`
- `a_M_se`: `0.0077526747927765954`
- `a_sqrtM`: `3.181201111844937`
- `a_sqrtM_se`: `0.6626098206476223`
- `a_logM`: `-24.660141990579493`
- `a_logM_se`: `5.245633593937816`
- `b_inv_sqrt`: `-340.40929621694755`
- `b_inv_sqrt_se`: `72.92933364391205`
- `b_inv`: `439.7091067432017`
- `b_inv_se`: `93.8941009001194`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0010581096671771779`
- `S_inf`: `-0.40441536828224567`
- `S_inf_se`: `0.013798131693377317`
- `alpha_inv_pred_blind`: `-0.20220768414112283`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.