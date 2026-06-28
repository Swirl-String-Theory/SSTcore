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

- input path: `outputs_routeB_BEM_v14_stageC\grids\C1_paired_fine\runs\g001_nc24_nt5_ns96_tf0p35_of2p4\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `rms`: `0.0010524354024426797`
- `S_ren`: `175.8776852333872`
- `S_ren_se`: `31.903255929102908`
- `alpha_inv_half_RT_only`: `87.9388426166936`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `192.63284605253278`
- `alpha_inv_pred_blind_with_soft`: `96.31642302626639`
- `a_M`: `-0.0631671067166657`
- `a_M_se`: `0.010028606314223575`
- `a_sqrtM`: `5.089515585400988`
- `a_sqrtM_se`: `0.8571303722690257`
- `a_logM`: `-38.22590140164347`
- `a_logM_se`: `6.785579891895257`
- `b_inv_sqrt`: `-506.2129362026145`
- `b_inv_sqrt_se`: `94.33899852924347`
- `b_inv`: `621.8670013543885`
- `b_inv_se`: `121.458335132621`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `162`
- `M_min`: `54`
- `M_max`: `215`
- `rms`: `0.0016042372798195125`
- `S_inf`: `-0.38844354645156387`
- `S_inf_se`: `0.02091983273664629`
- `alpha_inv_pred_blind`: `-0.19422177322578194`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=215, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=215, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=215, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.