# SST Schrödinger Gate Constants Audit

Tolerance: `2.000e-08` relative error.

Overall numerical gate status: **PASS**.

| status | quantity | value | unit | reference | relative error |
|---|---:|---:|---|---:|---:|
| INFO | Gamma_0 | `9.683619203488876e-09` | m^2 s^-1 | `` | `` |
| PASS | beta_0 = Gamma_0/(4*pi) | `7.705979316274285e-10` | m^2 s^-1 | `7.705979316274285e-10` | `0.000e+00` |
| PASS | Omega_0 = |v_swirl|/r_c | `7.763440655383073e+20` | s^-1 | `7.763440711050110e+20` | `7.170e-09` |
| PASS | lambda_Cbar(SST)=c/Omega_0 | `3.861592704932028e-13` | m | `3.861592677242833e-13` | `7.170e-09` |
| INFO | D_e = hbar/(2*m_e) | `5.788381802527148e-05` | m^2 s^-1 | `` | `` |
| PASS | D_SST = c^2/(2*Omega_0) | `5.788381844032207e-05` | m^2 s^-1 | `5.788381802527148e-05` | `7.170e-09` |
| PASS | R_SST = D_e/beta_0 | `7.511545989103091e+04` | dimensionless | `7.511546042963941e+04` | `7.170e-09` |
| PASS | R_SST = 4/alpha_SST^2 | `7.511546042963940e+04` | dimensionless | `7.511546042963941e+04` | `1.937e-16` |
| INFO | alpha_SST = 2|v_swirl|/c | `7.297352557148052e-03` | dimensionless | `` | `` |
| INFO | q_swirl = 0.5*rho_f*|v_swirl|^2 | `4.187743917945338e+05` | Pa | `` | `` |
| INFO | q_c = 0.5*rho_f*c^2 | `3.145643125578862e+10` | Pa | `` | `` |

## Interpretation

This audit supports the numerical identity

```tex
\frac{\hbar}{2m_e}=\frac{r_c c^2}{2\lVert\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert}
```

given the stated constants. This closes the constants gate only; the physical origin must still be established by the R-phase envelope and knot-boundary gates.
