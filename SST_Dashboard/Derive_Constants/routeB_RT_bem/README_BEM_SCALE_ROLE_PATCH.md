# Cursor patch: BEM scale-role correction

This patch updates the BEM source comments and README text so that the scale
roles are stated consistently across the Route-B BEM series.

Core correction:

```text
r_c is the horn-torus / return-flow circulation radius R_horn.
r_c is not, by default, the local ideal-tube radius a_tube.
```

Dimensionless BEM formulae remain unchanged:

```text
N_RT = M_max * L_cert^2
```

Physical reconstruction must use:

```text
a_tube = r_c / chi_h
ell_K_phys = 2 * a_tube * L_cert
```

This patch is intentionally conservative: it does not change numerical BEM
kernels or historical output values. It only prevents the wrong physical
interpretation from propagating into BEMv1--BEMv19 documentation and docstrings.
