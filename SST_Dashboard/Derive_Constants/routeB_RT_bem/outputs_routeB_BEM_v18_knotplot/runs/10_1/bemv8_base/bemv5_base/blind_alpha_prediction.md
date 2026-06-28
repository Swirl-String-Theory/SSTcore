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

- input path: `outputs_routeB_BEM_v18_knotplot\runs\10_1\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
- input sha256: `cd6d4465e7c0029f726ff87e715a4c236db5331787f4812b670758c1119c5bb4`
- source: `XML/Fourier ideal.txt=ideal.txt`
- target: `10_1`
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
- `rms`: `0.015442894495528083`
- `S_ren`: `8408.13892321893`
- `S_ren_se`: `468.13192926945504`
- `alpha_inv_half_RT_only`: `4204.069461609465`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `8424.894084038076`
- `alpha_inv_pred_blind_with_soft`: `4212.447042019038`
- `a_M`: `-3.1827491878567002`
- `a_M_se`: `0.1471545986464251`
- `a_sqrtM`: `251.4315562926716`
- `a_sqrtM_se`: `12.577089175394018`
- `a_logM`: `-1846.0073594876283`
- `a_logM_se`: `99.56810091935554`
- `b_inv_sqrt`: `-23901.081197391475`
- `b_inv_sqrt_se`: `1384.2818264375455`
- `b_inv`: `28769.81512231105`
- `b_inv_se`: `1782.2169899474807`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.07556781323387132`
- `S_inf`: `-15.199017167274281`
- `S_inf_se`: `0.9854315399680601`
- `alpha_inv_pred_blind`: `-7.5995085836371405`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `10_1`: `raw_spectrum_10_1.npy`, modes=215, Id=10:1:1, L=42.58107

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.