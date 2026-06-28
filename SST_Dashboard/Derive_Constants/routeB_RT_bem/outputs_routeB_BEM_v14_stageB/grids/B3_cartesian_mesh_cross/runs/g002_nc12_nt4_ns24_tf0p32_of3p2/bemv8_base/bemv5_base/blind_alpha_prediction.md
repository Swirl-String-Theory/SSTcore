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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g002_nc12_nt4_ns24_tf0p32_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.0015898413198896346`
- `S_ren`: `150.6467863551475`
- `S_ren_se`: `64.35324980438696`
- `alpha_inv_half_RT_only`: `75.32339317757375`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `167.40194717429307`
- `alpha_inv_pred_blind_with_soft`: `83.70097358714654`
- `a_M`: `-0.2819074751830102`
- `a_M_se`: `0.0801359385982672`
- `a_sqrtM`: `11.945141972327164`
- `a_sqrtM_se`: `3.936512713499881`
- `a_logM`: `-46.28172767708971`
- `a_logM_se`: `17.907946624211643`
- `b_inv_sqrt`: `-309.2298197997312`
- `b_inv_sqrt_se`: `143.03943328233527`
- `b_inv`: `187.44932077755573`
- `b_inv_se`: `105.7805752642068`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.003975920570755079`
- `S_inf`: `-0.6354763150644085`
- `S_inf_se`: `0.09000930903617381`
- `alpha_inv_pred_blind`: `-0.31773815753220425`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.