# Interior one-cell phase Hessian

Problem:
\[

abla\cdot(n_{eff}(r)
abla	heta)=0,\quad
	heta(a)=0,\quad 	heta(R)=\phi.
\]

Analytic radial Hessian:
\[
\Lambda_\phi=rac{4\pi}{\int_a^R dr/[n_{eff}(r)r^2]}.
\]

Parameters:
- a = 0.0152703116982
- R = 1.0
- density mode = constant
- n0 = 1.0

Result:
\[
\Lambda_\phi=0.194866720917.
\]

Target:
\[
E_{eff}/2=137.037437828.
\]

Ratio:
\[
\Lambda_\phi/(E_{eff}/2)=0.00142199623697.
\]

Required n0 if used diagnostically:
\[
n0_{required}=703.236741419.
\]

Status: `OPEN_INTERIOR_HESSIAN_GATE`.

If n0_required is solved from the target, this is not a derivation.  The gate
closes only when n_eff and n0 are supplied independently by the interior
finite-cell GP/Hodge model.
