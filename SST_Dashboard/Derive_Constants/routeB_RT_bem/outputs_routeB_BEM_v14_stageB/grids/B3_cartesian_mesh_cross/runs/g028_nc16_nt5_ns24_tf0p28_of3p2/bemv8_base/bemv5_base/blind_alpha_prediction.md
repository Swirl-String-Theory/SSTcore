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

- input path: `outputs_routeB_BEM_v14_stageB\grids\B3_cartesian_mesh_cross\runs\g028_nc16_nt5_ns24_tf0p28_of3p2\bemv8_base\bemv5_base\idealxml_sampled_ideal_used.txt`
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
- `n_points`: `78`
- `M_min`: `26`
- `M_max`: `103`
- `rms`: `0.0011211335726374926`
- `S_ren`: `-127.90992903092527`
- `S_ren_se`: `41.390251052175685`
- `alpha_inv_half_RT_only`: `-63.954964515462635`
- `soft_action`: `16.755160819145562`
- `S_total_soft_plus_RT`: `-111.15476821177971`
- `alpha_inv_pred_blind_with_soft`: `-55.577384105889855`
- `a_M`: `0.08339919912505467`
- `a_M_se`: `0.03220414101783037`
- `a_sqrtM`: `-5.408375388528118`
- `a_sqrtM_se`: `1.9050851251522938`
- `a_logM`: `31.477335677649528`
- `a_logM_se`: `10.437663637389893`
- `b_inv_sqrt`: `315.29880111280005`
- `b_inv_sqrt_se`: `100.41687771906406`
- `b_inv`: `-287.7766379710012`
- `b_inv_se`: `89.4521389187057`

## Legacy inverse-tail fit retained for comparison

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `78`
- `M_min`: `26`
- `M_max`: `103`
- `rms`: `0.0017937409028529736`
- `S_inf`: `-0.6762741215880212`
- `S_inf_se`: `0.03372273890251387`
- `alpha_inv_pred_blind`: `-0.3381370607940106`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=103, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=103, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=103, Id=4:1:1, L=21.043322

## Interpretation

A small RMS counterterm fit is not an alpha derivation. Route B still requires stability under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, and a theorem-level map from the R--T spectral action to fine structure.