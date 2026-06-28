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

- input path: `/mnt/data/outputs_routeB_BEM_v6_fast/runs/g003_nc12_nt4_ns24_tf0p28_of3p0/idealxml_sampled_ideal_used.txt`
- input sha256: `f05c65f845f5e00742e92da382adbfe5b1095401368ce8776282a1966a5a2a21`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
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
- `rms`: `0.004011232542576038`
- `S_ren`: `987.4495387848843`
- `S_ren_se`: `162.3669596106057`
- `alpha_inv_half_RT_only`: `493.72476939244217`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `1004.2046996040299`
- `alpha_inv_pred_blind_with_soft`: `502.10234980201494`
- `a_M`: `-1.54306216131096`
- `a_M_se`: `0.20218758786621993`
- `a_sqrtM`: `69.35631166033531`
- `a_sqrtM_se`: `9.93204850779528`
- `a_logM`: `-288.939512754689`
- `a_logM_se`: `45.182782004736936`
- `b_inv_sqrt`: `-2115.0456247072275`
- `b_inv_sqrt_se`: `360.89673474424035`
- `b_inv`: `1435.4262108731477`
- `b_inv_se`: `266.8904808375814`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `54`
- `M_min`: `18`
- `M_max`: `71`
- `rms`: `0.013794862048164944`
- `S_inf`: `-2.6022946809018705`
- `S_inf_se`: `0.31229648055551756`
- `alpha_inv_pred_blind`: `-1.3011473404509353`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=71, Id=0:1:1, L=6.283185307179586
- `3_1`: `raw_spectrum_3_1.npy`, modes=71, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=71, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.