# BEMv18 multi-knot exponent test

This report is alpha-blind. It does not contain or compare against observed fine structure.

## Goal

Test whether the BEMv17 target exponent

\[
b=2
\]

is empirically consistent across several knots with different certified lengths.

The canonical normalizer is

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]

## Targets

- `3_1` / `3:1:1`: `L_cert=16.371637`
- `4_1` / `4:1:1`: `L_cert=21.043322`
- `5_1` / `5:1:1`: `L_cert=23.598564`
- `6_1` / `6:1:1`: `L_cert=28.354929`
- `7_1` / `7:1:1`: `L_cert=30.700289`

## Valid budgets collected

- `5` valid BEMv13 budgets

## Certificate

- `selected_exponent_a`: `1.0`
- `selected_exponent_b`: `3.0`
- `selected_formula`: `M^1 L^3`
- `selected_score`: `0.03589632416576362`
- `canonical_formula`: `M^1 L^2`
- `canonical_score`: `1.0358963241657713`
- `canonical_slope_logR_vs_logL`: `1.02135510269923`
- `canonical_corr_logR_logL`: `0.9788340963643252`
- `canonical_max_subleading_ratio`: `3.1426358054892974e-06`
- `canonical_gate`: `PASS_MULTIKNOT_EXPONENT_DIAGNOSTIC`
- `certificate_status`: `PASS_CANONICAL_SUBLEADING_BUT_NOT_BEST_SCORE`
- `interpretation`: `Multi-knot exponent diagnostic is a falsifier; shape factors remain a confounder.`
- `n_targets_requested`: `5`
- `n_valid_budgets`: `5`
- `uses_observed_alpha`: `no`
- `next_gate`: `BEMv19_MULTI_KNOT_PRODUCTION_OR_Q_MINUS_2_SYMBOL_DERIVATION`

## Interpretation

If the status is `FAIL_NOT_ENOUGH_KNOTS`, run BEMv18 with at least three target knots. If the canonical candidate passes but is not best-score, this supports subleading behavior but does not uniquely identify b=2. If it is selected, that is strong empirical support for the q_{-2} route.

## Next gate

\[
\boxed{\text{BEMv19: multi-knot production grid or explicit }q_{-2}\text{ symbolic derivation.}}
\]