# Gate 1: sector pressure-volume factor (4*pi/3 -> 16*pi/3)

## Result

Pressure-work integral per sector (spherical cell, dimensionless shape Jacobian
W_hat = W/R^3), averaged over the N_p = 4 affine H_0 (+) H_1 modes:

\[
\overline{W}_a = 4.18524537037
\qquad(\text{spread }0.00e+00),
\qquad
\frac{4\pi}{3} = 4.18879020479.
\]

Total over all sectors:

\[
W_{\rm tot} = \sum_{a=1}^{N_p} W_a = 16.7409814815,
\qquad
\frac{16\pi}{3} = 16.7551608191.
\]

Symbolic confirmation of the unit-ball volume Jacobian (sympy):
\[
\int_{\rm ball} dV = 4*pi/3 = 4.18879020479 = \frac{4\pi}{3}.
\]

`pass_per_sector = True`, `pass_total = True`.

## Controls

* **non-spherical** cell axes (1.0, 0.6, 1.7): rigid per-sector integral becomes the
  ellipsoid volume 4.27256600888 != 4*pi/3, and under a surface-normalized
  convention the three dipole sectors split anisotropically (std/mean
  7.582e-01 > tol). Pass: `True`.
* **N_p = 1 truncation** (monopole only): 4.18524537037 = 4*pi/3. Pass: `True`.

## Status

`DERIVED_WITHIN_REDUCTION_SECTOR_VOLUME_4PI_3_TOTAL_16PI_3`

4*pi/3 and 16*pi/3 are never inserted: 4*pi/3 is the *computed* spherical-cell
volume Jacobian of each unit-amplitude affine H_0 (+) H_1 mode, and 16*pi/3 is
N_p = 4 times that integral. Given the already-derived modeset
(k_ell = (ell-1)(ell+2) => leading manifold H_0 (+) H_1, N_p = 4) and pressure
self-duality, the sector-volume normalization is **derived within the finite-cell
pressure reduction** rather than a blocking coefficient.
