# Full-field GP Schur w_perp convergence study

| n | L_box | R_mask | dx | H_scalar | H_perp | w_perp |
|---|-------|--------|----|----------|--------|--------|
| 61 | 8.0 | 7.0 | 0.2667 | 0.54763 | 219.86 | 401.46507 |
| 81 | 8.0 | 7.0 | 0.2000 | 0.40249 | 288.79 | 717.51260 |
| 101 | 8.0 | 7.0 | 0.1600 | 0.3306 | 350.19 | 1059.27132 |
| 121 | 8.0 | 7.0 | 0.1333 | 0.29368 | 419.44 | 1428.21601 |
| 81 | 10.0 | 9.0 | 0.2500 | 0.40247 | 301.27 | 748.54922 |
| 101 | 12.0 | 11.0 | 0.2400 | 0.34138 | 374.54 | 1097.13912 |

Richardson extrapolation (dx->0): **w_perp = 2266.72667**
Spread across runs: 3.285e+02  (converged: False)
sigma = 1514.15111, c2 = 94.634445 (target 11/48 = 0.229167)

## Verdict: `FALSIFIER_BARE_GP_WPERP_DIVERGES_NO_FINITE_VALUE`

Bare 2D GP gives **no finite** w_perp. Under grid refinement (dx -> 0) and box
enlargement the transverse (shear) stiffness H_perp grows without bound, while
the volumetric (scalar) stiffness H_scalar -- a localized potential-dilation
response ~ int 1/4 (1-|psi|^2)^2 -- stays finite. The ratio therefore diverges.

Mechanism: the perp channel deforms the vortex phase circulation, whose energy
int 1/2 |grad theta|^2 ~ pi n^2 ln(R/xi) is logarithmically (and, at the core
cusp, power-) divergent. It is dominated by non-core far-field circulation, not
by the core shell that the 11/48 reduction is about. By contrast the volumetric
channel only feels the finite, core-localized depletion. The two second
variations are not commensurate in bare GP.

Consequence: 11/48 is NOT a bare-GP result. Closing w_perp = 1 requires an
SST-specific transverse term that (a) regulates the transverse sector to a
core-localized stiffness (removing the far-field phase divergence) and
(b) sets that stiffness equal to the volumetric one. Candidate: a swirl /
internal-pressure self-duality coupling in the primitive action that ties the
shear response to the dilation response. Deriving and justifying that term is
the open primitive-equation gate; bare GP alone cannot supply w_perp = 1.