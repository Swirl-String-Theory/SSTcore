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

- input path: `outputs_routeB_BEM_v14_stageD\grids\D3_ultra_tube_anchored\runs\g004_nc64_nt10_ns384_tf0p14_of4p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0007186753469711894`
- `S_ren`: `285.70244516412026`
- `S_ren_se`: `13.356608128791425`
- `alpha_inv_half_RT_only`: `142.85122258206013`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `302.4576059832658`
- `alpha_inv_pred_blind_with_soft`: `151.2288029916329`
- `a_M`: `-0.014296838232543962`
- `a_M_se`: `0.0006622937653124224`
- `a_sqrtM`: `2.637993605305828`
- `a_sqrtM_se`: `0.12349082910514868`
- `a_logM`: `-45.55459082604371`
- `a_logM_se`: `2.133000017459238`
- `b_inv_sqrt`: `-1393.2410040925522`
- `b_inv_sqrt_se`: `64.70694270172466`
- `b_inv`: `3964.0393268346397`
- `b_inv_se`: `181.79544234342117`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `768`
- `M_min`: `256`
- `M_max`: `1023`
- `rms`: `0.0009937767770763699`
- `S_inf`: `-0.3443827031558225`
- `S_inf_se`: `0.005957688828150784`
- `alpha_inv_pred_blind`: `-0.17219135157791124`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=1023, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=1023, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=1023, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.