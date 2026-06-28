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

- scenarios = 40
- pass = 30
- frequency_bound_fail = 10
- neutrality_bound_fail = 0
- max |epsilon| = 6.931471805599e-09
- max |delta_nu/nu| = 2.079441518976e-08
- max |delta S_t/S_t0| = 9.237117051210e-14

## First 25 scenarios

| name | epsilon | delta_nu/nu | delta S_t/S_t0 | chi_residual_abs | status |
|---|---:|---:|---:|---:|---|
| scan_lambda_1.000e-25 | 6.931e-26 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_2.728e-25 | 1.891e-25 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_7.444e-25 | 5.160e-25 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_2.031e-24 | 1.408e-24 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_5.541e-24 | 3.841e-24 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.512e-23 | 1.048e-23 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_4.125e-23 | 2.859e-23 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.125e-22 | 7.800e-23 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_3.070e-22 | 2.128e-22 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_8.377e-22 | 5.806e-22 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_2.285e-21 | 1.584e-21 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_6.236e-21 | 4.322e-21 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.701e-20 | 1.179e-20 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_4.642e-20 | 3.217e-20 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.266e-19 | 8.778e-20 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_3.455e-19 | 2.395e-19 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_9.427e-19 | 6.534e-19 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_2.572e-18 | 1.783e-18 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_7.017e-18 | 4.864e-18 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.914e-17 | 1.327e-17 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_5.223e-17 | 3.621e-17 | 0.000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_1.425e-16 | 9.878e-17 | 0.000e+00 | 0.000e+00 | 2.776e-17 | PASS |
| scan_lambda_3.888e-16 | 2.695e-16 | -6.661e-16 | 0.000e+00 | 2.776e-17 | PASS |
| scan_lambda_1.061e-15 | 7.353e-16 | -1.998e-15 | 0.000e+00 | 0.000e+00 | PASS |
| scan_lambda_2.894e-15 | 2.006e-15 | -5.995e-15 | 0.000e+00 | 2.776e-17 | PASS |

## Interpretation

A PASS means this specific parameter point is internally consistent, keeps the holonomy partition closed, and does not exceed the chosen proxy bounds.

A frequency-bound failure means the entanglement-weighted attachment would produce a transition shift larger than the selected spectroscopic tolerance.

A neutrality-bound failure only matters if --neutrality-mode charge-leak is selected. For a charge-neutral phase-clock coupling, use --neutrality-mode compensated.
