# SST R-phase Envelope Symbolic Gate

```text
Symbolic one-dimensional envelope derivation
====================================================
Ansatz:
  theta(x,t) = psi(x,t) exp(-i Omega_0 t)

Carrier equation residual divided by exp(-i Omega_0 t):
  -2*I*Omega_0*Derivative(psi(x, t), t) - c**2*Derivative(psi(x, t), (x, 2)) + Derivative(psi(x, t), (t, 2))

After SVEA, psi_tt -> 0:
  -2*I*Omega_0*Derivative(psi(x, t), t) - c**2*Derivative(psi(x, t), (x, 2)) = 0

Equivalent Schrödinger-type envelope:
  Eq(I*Derivative(psi(x, t), t), -c**2*Derivative(psi(x, t), (x, 2))/(2*Omega_0))

In vector form:
  i partial_t psi = - c^2/(2 Omega_0) nabla^2 psi

Numerical closure
====================================================
Omega_0 = |v_swirl|/r_c              7.763440655383073e+20 s^-1
D_SST = c^2/(2 Omega_0)              5.788381844032207e-05 m^2 s^-1
D_e = hbar/(2 m_e)                   5.788381802527148e-05 m^2 s^-1
relative error D_SST vs D_e          7.170407957579915e-09 dimensionless
lambda_Cbar(SST)                     3.861592704932028e-13 m
lambda_Cbar(std)                     3.861592677242833e-13 m
relative error lambda_Cbar           7.170407988949594e-09 dimensionless

Gate interpretation
====================================================
PASS here means: if Omega_0 = |v_swirl|/r_c is accepted as the horn-torus core-cycle frequency, then the R-phase envelope coefficient equals the electron Schrödinger coefficient within the constants tolerance.
This supports [CANON-CANDIDATE] status for the R-phase stiffness route.

```

## Canon-candidate equation

```tex
\partial_t^2\theta_R-c^2\nabla^2\theta_R+\Omega_0^2\theta_R=0,\qquad \Omega_0=\frac{\lVert\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert}{r_c}.
\theta_R=\psi e^{-i\Omega_0 t}+\mathrm{c.c.}\quad\Longrightarrow\quad i\partial_t\psi=-\frac{c^2}{2\Omega_0}\nabla^2\psi.
```
