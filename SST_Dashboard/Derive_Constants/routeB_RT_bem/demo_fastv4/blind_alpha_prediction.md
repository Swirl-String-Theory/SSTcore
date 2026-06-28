# Blind Route-B alpha prediction audit

## Status

This file is alpha-blind. It does not contain or compare against CODATA alpha.
The printed quantity is a candidate prediction under the provisional map

\[
\alpha_{\rm inv,pred}^{\rm blind}=\frac12 S_{\rm ren}(K/{\rm ref}).
\]

This map is a Route-B working hypothesis, not yet a theorem.

## Provenance

- input path: `/mnt/data/outputs_routeB_BEM_v4_fast/idealxml_sampled_ideal_used.txt`
- input sha256: `9defe945e4033d8c9aadbc3d456fb3b4892ae4a36d2203ab12fe0d5f0afef126`
- source: `XML/Fourier ideal.txt=/mnt/data/ideal.txt`
- target: `3_1`
- reference/vacuum subtraction: `0_1`
- BEM backend: `BEM_V4_AREA_SYMMETRIC_ZETA_CUTOFF`
- scipy generalized eigensolver: `True`

## Mesh/operator parameters

- `n_center`: `10`
- `n_theta`: `3`
- `n_sphere`: `18`
- `boundary_subspace`: `all`
- `tube_fraction`: `0.3`
- `outer_factor`: `2.6`
- `mu_mode`: `inverse_outer_radius`
- `mu_value`: `1.0`
- `ridge_rel`: `1e-09`
- `self_scale`: `1.0`
- `keep_constant`: `False`
- `max_raw_modes`: `0`

## Selected renormalized cutoff fit

- `model`: `sqrt+inv+threehalf`
- `status`: `PASS_FIT`
- `n_points`: `36`
- `M_min`: `12`
- `M_max`: `47`
- `rms`: `0.0022629075359335516`
- `S_inf`: `-0.16776969212666007`
- `S_inf_se`: `0.06314352587243344`
- `alpha_inv_pred_blind`: `-0.08388484606333003`
- `c_sqrt`: `0.14866211961057052`
- `c_sqrt_se`: `0.926864157047283`
- `c_inv`: `5.835733786607684`
- `c_inv_se`: `4.438026042450955`
- `c_threehalf`: `-14.975921213587744`
- `c_threehalf_se`: `6.934490709761417`

## Raw spectra saved

- `0_1`: `raw_spectrum_0_1.npy`, modes=47, Id=0:1:1, L=6.283185
- `3_1`: `raw_spectrum_3_1.npy`, modes=47, Id=3:1:1, L=16.371637
- `4_1`: `raw_spectrum_4_1.npy`, modes=47, Id=4:1:1, L=21.043322

## Interpretation

If the target fit is unstable under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, or model choice, Route B is not yet a derivation.
Only after a canonical theorem-level map and stable continuum/renormalized limit exist should this blind number be compared with observed alpha.