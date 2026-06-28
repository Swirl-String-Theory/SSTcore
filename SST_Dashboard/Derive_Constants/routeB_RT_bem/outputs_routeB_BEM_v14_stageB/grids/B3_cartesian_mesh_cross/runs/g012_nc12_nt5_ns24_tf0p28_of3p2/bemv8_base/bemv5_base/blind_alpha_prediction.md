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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g012_nc12_nt5_ns24_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `63`
- `M_min`: `21`
- `M_max`: `83`
- `rms`: `0.010702564755992013`
- `S_ren`: `6564.7216497868485`
- `S_ren_se`: `416.9582745271723`
- `alpha_inv_half_RT_only`: `3282.3608248934243`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `6581.476810605994`
- `alpha_inv_pred_blind_with_soft`: `3290.738405302997`
- `a_M`: `-8.122483611433083`
- `a_M_se`: `0.4257302651255405`
- `a_sqrtM`: `397.92693460111735`
- `a_sqrtM_se`: `22.60930127236002`
- `a_logM`: `-1818.6255901575623`
- `a_logM_se`: `111.2003064198036`
- `b_inv_sqrt`: `-14692.205371001955`
- `b_inv_sqrt_se`: `960.3248651035556`
- `b_inv`: `11044.509454785139`
- `b_inv_se`: `767.87213157993`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `63`
- `M_min`: `21`
- `M_max`: `83`
- `rms`: `0.08041889305950611`
- `S_inf`: `-22.549745051697016`
- `S_inf_se`: `1.6837021362252478`
- `alpha_inv_pred_blind`: `-11.274872525848508`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=83, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=83, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=83, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.