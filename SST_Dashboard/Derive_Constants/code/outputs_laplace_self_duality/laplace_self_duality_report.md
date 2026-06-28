# Laplace-matched pressure self-duality audit

## SST pressure identity

\[
P_{\rm kin}=\frac12\rho_{\rm core}\lVert\mathbf v_{\circlearrowleft}\rVert^2
= 2.329244600448e+30\,\mathrm{Pa}.
\]

\[
P_{\rm Laplace}=\frac{F_{\rm swirl}^{\max}}{2\pi r_c^2}
= 2.329244600448e+30\,\mathrm{Pa}.
\]

Ratio:

\[
\mu=P_{\rm Laplace}/P_{\rm kin}
= 1.
\]

## Radius action

The matched reciprocal action is

\[
A_\chi=\chi_R+\mu\frac{N_p}{\chi_R}.
\]

Stationarity gives

\[
\chi_R=\sqrt{\mu N_p}=2.
\]

For \(N_p=4\) and \(\mu=1\), this gives

\[
\chi_R=2,\qquad \lambda_\chi=4.
\]

## Status

- Pressure match within tolerance: `True`.
- Self-duality exact within tolerance: `True`.
- Higher-order primitive-equation terms remain an open gate.
