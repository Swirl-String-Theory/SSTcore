# SST Attachment Lemma / Swirl-Clock Entanglement Audit

## Model

```text
epsilon = lambda_SE * s * A
denom   = 1 + sigma * epsilon
chi_3   = chi_total / denom
chi_att = sigma * epsilon * chi_3
S_t     = sqrt(1 - (u_theta0 / (c * denom))^2)
delta_nu/nu = denom^(-kappa) - 1
```

## Constants

- c = 2.997924580000e+08 m s^-1
- |v_swirl| = 1.093845630000e+06 m s^-1
- r_c = 1.408970170000e-15 m
- rho_f = 7.000000000000e-07 kg m^-3
- Gamma_core = 2*pi*r_c*|v_swirl| = 9.683619203489e-09 m^2 s^-1

## Audit settings

- kappa = 3.0
- frequency_tolerance = 1.000e-12
- neutrality_mode = compensated
- neutrality_tolerance = 1.000e-20
- closure_tolerance = 1.000e-14

## Summary

- scenarios = 1
- pass = 1
- frequency_bound_fail = 0
- neutrality_bound_fail = 0
- max |epsilon| = 6.931471805599e-14
- max |delta_nu/nu| = 2.078337502098e-13
- max |delta S_t/S_t0| = 0.000000000000e+00

## First 25 scenarios

| name | epsilon | delta_nu/nu | delta S_t/S_t0 | chi_residual_abs | status |
|---|---:|---:|---:|---:|---|
| single | 6.931e-14 | -2.078e-13 | 0.000e+00 | 0.000e+00 | PASS |

## Interpretation

A PASS means this specific parameter point is internally consistent, keeps the holonomy partition closed, and does not exceed the chosen proxy bounds.

A frequency-bound failure means the entanglement-weighted attachment would produce a transition shift larger than the selected spectroscopic tolerance.

A neutrality-bound failure only matters if --neutrality-mode charge-leak is selected. For a charge-neutral phase-clock coupling, use --neutrality-mode compensated.
