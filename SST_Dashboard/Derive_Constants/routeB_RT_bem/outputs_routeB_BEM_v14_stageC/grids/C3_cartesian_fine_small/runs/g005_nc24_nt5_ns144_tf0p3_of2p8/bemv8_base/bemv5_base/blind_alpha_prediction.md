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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g005_nc24_nt5_ns144_tf0p3_of2p8\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0007566263463236759`
- `S_ren`: `132.0791263397896`
- `S_ren_se`: `21.640742232808744`
- `alpha_inv_half_RT_only`: `66.0395631698948`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `148.83428715893518`
- `alpha_inv_pred_blind_with_soft`: `74.41714357946759`
- `a_M`: `-0.03640883911186765`
- `a_M_se`: `0.00533211565970988`
- `a_sqrtM`: `3.2547064762183235`
- `a_sqrtM_se`: `0.5040502766670136`
- `a_logM`: `-27.333000258193156`
- `a_logM_se`: `4.4135753827108415`
- `b_inv_sqrt`: `-407.93469808748364`
- `b_inv_sqrt_se`: `67.87039697074663`
- `b_inv`: `568.9279381617855`
- `b_inv_se`: `96.65206143111699`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `198`
- `M_min`: `66`
- `M_max`: `263`
- `rms`: `0.0011875982496513914`
- `S_inf`: `-0.4219888075881879`
- `S_inf_se`: `0.014010099500262281`
- `alpha_inv_pred_blind`: `-0.21099440379409395`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=263, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=263, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=263, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.