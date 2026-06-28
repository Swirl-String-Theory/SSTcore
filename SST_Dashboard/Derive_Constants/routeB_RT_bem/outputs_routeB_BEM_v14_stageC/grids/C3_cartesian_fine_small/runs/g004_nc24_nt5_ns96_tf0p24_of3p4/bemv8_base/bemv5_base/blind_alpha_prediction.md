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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C3_cartesian_fine_small\runs\g004_nc24_nt5_ns96_tf0p24_of3p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0006503422500124908`
- `S_ren`: `-57.3236004848582`
- `S_ren_se`: `19.714307591232096`
- `alpha_inv_half_RT_only`: `-28.6618002424291`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-40.56843966571263`
- `alpha_inv_pred_blind_with_soft`: `-20.284219832856316`
- `a_M`: `0.013221337357057217`
- `a_M_se`: `0.006197080010558511`
- `a_sqrtM`: `-1.331554752161596`
- `a_sqrtM_se`: `0.5296554007606582`
- `a_logM`: `11.751307018486504`
- `a_logM_se`: `4.193083285009528`
- `b_inv_sqrt`: `175.894506164063`
- `b_inv_sqrt_se`: `58.295869204927094`
- `b_inv`: `-237.95596446743176`
- `b_inv_se`: `75.05400024513337`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0010219882685823462`
- `S_inf`: `-0.30916523428568377`
- `S_inf_se`: `0.013327095627626108`
- `alpha_inv_pred_blind`: `-0.15458261714284188`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.