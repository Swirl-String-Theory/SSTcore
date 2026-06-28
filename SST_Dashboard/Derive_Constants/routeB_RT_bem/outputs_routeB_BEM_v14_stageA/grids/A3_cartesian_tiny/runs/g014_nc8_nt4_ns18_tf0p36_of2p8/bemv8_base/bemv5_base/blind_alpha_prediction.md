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

- input path: `outputs_routeB_BEM_v14_stageA\grids\A3_cartesian_tiny\runs\g014_nc8_nt4_ns18_tf0p36_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `37`
- `M_min`: `13`
- `M_max`: `49`
- `rms`: `0.04217191592760559`
- `S_ren`: `19628.42838407994`
- `S_ren_se`: `2186.9494787684307`
- `alpha_inv_half_RT_only`: `9814.21419203997`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `19645.183544899086`
- `alpha_inv_pred_blind_with_soft`: `9822.591772449543`
- `a_M`: `-44.88330279813442`
- `a_M_se`: `4.294385951000615`
- `a_sqrtM`: `1740.6883812192139`
- `a_sqrtM_se`: `176.80649276925598`
- `a_logM`: `-6271.386999094102`
- `a_logM_se`: `674.5274648558827`
- `b_inv_sqrt`: `-39798.3558490883`
- `b_inv_sqrt_se`: `4521.0239152712775`
- `b_inv`: `23453.763053627914`
- `b_inv_se`: `2807.2052242856344`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `37`
- `M_min`: `13`
- `M_max`: `49`
- `rms`: `0.18151191539811978`
- `S_inf`: `-35.793551100323086`
- `S_inf_se`: `5.437061126792325`
- `alpha_inv_pred_blind`: `-17.896775550161543`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=49, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=49, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=49, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.