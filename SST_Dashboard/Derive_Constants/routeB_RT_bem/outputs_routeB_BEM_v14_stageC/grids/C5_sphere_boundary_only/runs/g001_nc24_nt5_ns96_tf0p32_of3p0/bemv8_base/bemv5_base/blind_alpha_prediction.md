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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C5_sphere_boundary_only\runs\g001_nc24_nt5_ns96_tf0p32_of3p0\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `1.3543634662870429e-15`
- `S_ren`: `-1.2488729443396343e-10`
- `S_ren_se`: `5.1027030611763615e-11`
- `alpha_inv_half_RT_only`: `-6.244364721698171e-11`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `16.755160819020674`
- `alpha_inv_pred_blind_with_soft`: `8.377580409510337`
- `a_M`: `1.2511765561805121e-13`
- `a_M_se`: `4.3940482178071694e-14`
- `a_sqrtM`: `-6.658352751983028e-12`
- `a_sqrtM_se`: `2.4964264602804455e-12`
- `a_logM`: `3.3070778755323166e-11`
- `a_logM_se`: `1.3135658171371588e-11`
- `b_inv_sqrt`: `2.9123061098768474e-10`
- `b_inv_sqrt_se`: `1.2136455655078915e-10`
- `b_inv`: `-2.4059726914511387e-10`
- `b_inv_se`: `1.0382565473710436e-10`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `72`
- `M_min`: `24`
- `M_max`: `95`
- `rms`: `1.8019719151130395e-15`
- `S_inf`: `3.55908429856493e-13`
- `S_inf_se`: `3.526951875866246e-14`
- `alpha_inv_pred_blind`: `1.779542149282465e-13`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=95, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=95, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=95, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.