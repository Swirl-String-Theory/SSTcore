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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B2_paired_medium\runs\g003_nc24_nt6_ns72_tf0p26_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0006100825958673188`
- `S_ren`: `198.43355857592638`
- `S_ren_se`: `18.49388679692064`
- `alpha_inv_half_RT_only`: `99.21677928796319`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `215.18871939507196`
- `alpha_inv_pred_blind_with_soft`: `107.59435969753598`
- `a_M`: `-0.0696523272058851`
- `a_M_se`: `0.005813447703215335`
- `a_sqrtM`: `5.665997190844726`
- `a_sqrtM_se`: `0.49686690631740615`
- `a_logM`: `-42.95436341230531`
- `a_logM_se`: `3.933509064123305`
- `b_inv_sqrt`: `-574.4221000973026`
- `b_inv_sqrt_se`: `54.68704395601012`
- `b_inv`: `714.0620979911355`
- `b_inv_se`: `70.40775729840387`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0013246853439904853`
- `S_inf`: `-0.37463254712813854`
- `S_inf_se`: `0.017274374666125147`
- `alpha_inv_pred_blind`: `-0.18731627356406927`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.