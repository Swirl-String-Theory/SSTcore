# Finite-core / nonspherical correction audit

## Baseline

The spherical fixed-volume surface spectrum gives

\[
k_\ell=\ell(\ell+1)-2=(\ell-1)(\ell+2).
\]

Thus the first positive shape-mode gap is

\[
k_2=4.
\]

## Finite-core scale

Using

\[
\eta_K=\frac{1}{4\mathcal L_K},
\qquad
\mathcal L_K=16.371637,
\]

gives

\[
\eta_K=0.0152703116982,
\qquad
\eta_K^2=0.000233182419361.
\]

## Criterion

If

\[
\|\delta H\|_{op}<\frac{k_2}{2}=2,
\]

then the \(\ell\ge2\) block remains separated from the retained
\(\ell=1\) translation sector.

## Selected audit

Selected amplitude: `0.5`  
Operator norm: `0.5`  
Minimum projected \(\ell\ge2\) eigenvalue: `3.91672639829`  
Mean \(\ell\ge2\) leakage into lowest three shape modes: `0.00024754418927`  
Status: `PASS_NO_LEADING_PROMOTION`

For the physical perturbative scale \(\eta_K\), the correction is far below
the half-gap threshold. Therefore perturbative finite-core/nonspherical
corrections cannot promote \(\ell\ge2\) shape modes into the leading pressure
manifold. Large nonperturbative nonspherical cells remain outside this audit.
