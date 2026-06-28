# Phase-pressure exchange self-duality gate

## Canonical normal-mode derivation

The linearized GP/Madelung Hamiltonian reduces mode by mode to

\[
H_k=\frac12p_k^2+\frac12\omega_k^2 q_k^2.
\]

For a periodic normal mode,

\[
\left\langle\frac12p_k^2\right\rangle_T
=
\left\langle\frac12\omega_k^2 q_k^2\right\rangle_T.
\]

Identifying the phase/flow sector with the kinetic part and the
pressure/compression sector with the potential part gives

\[
M_\phi=M_p=\frac{E_{eff}}{2}.
\]

## Numerical values

\[
E_{eff}=274.074875657,
\qquad
M_\phi=M_p=137.037437828.
\]

With the accessible-area projection and radial optimum,

\[
\Lambda_\phi=137.037437828,
\qquad
\frac{\Lambda_\phi}{E_{eff}/2}=1.
\]

## Sensitivity

For a noncanonical split \(\gamma=1.05\),

\[
\frac{\Lambda_\phi}{E_{eff}/2}
=
1.0243902439.
\]

## Status

`PHASE_PRESSURE_HALF_BUDGET_DERIVED_WITHIN_CANONICAL_NORMAL_MODE_REDUCTION`

This closes the half-budget gate inside the canonical linearized normal-mode
reduction.  The remaining physical identification is that the finite-cell
\(E_{eff}\) used in the pressure-cell chain is the cycle-averaged quadratic
energy of the same canonical interior mode family.
