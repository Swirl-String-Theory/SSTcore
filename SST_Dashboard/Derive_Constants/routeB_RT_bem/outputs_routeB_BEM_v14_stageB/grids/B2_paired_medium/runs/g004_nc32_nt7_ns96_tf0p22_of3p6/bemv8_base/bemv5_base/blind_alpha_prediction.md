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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B2_paired_medium\runs\g004_nc32_nt7_ns96_tf0p22_of3p6\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0005429006986106947`
- `S_ren`: `189.96554155664703`
- `S_ren_se`: `14.661963824790158`
- `alpha_inv_half_RT_only`: `94.98277077832351`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `206.7207023757926`
- `alpha_inv_pred_blind_with_soft`: `103.3603511878963`
- `a_M`: `-0.04016977313819403`
- `a_M_se`: `0.0028653899001798303`
- `a_sqrtM`: `4.028882203042327`
- `a_sqrtM_se`: `0.2983214332009795`
- `a_logM`: `-37.683826535248144`
- `a_logM_se`: `2.876965020694012`
- `b_inv_sqrt`: `-621.8093297639056`
- `b_inv_sqrt_se`: `48.726487784455735`
- `b_inv`: `951.8054784297855`
- `b_inv_se`: `76.42648928364775`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `240`
- `M_min`: `80`
- `M_max`: `319`
- `rms`: `0.0010089509480372372`
- `S_inf`: `-0.2855119114456515`
- `S_inf_se`: `0.01081261453082047`
- `alpha_inv_pred_blind`: `-0.14275595572282576`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=319, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=319, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=319, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.