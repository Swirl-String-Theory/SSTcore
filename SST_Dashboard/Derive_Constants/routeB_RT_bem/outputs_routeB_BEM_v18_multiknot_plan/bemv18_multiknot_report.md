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

## Valid budgets collected

- `0` valid BEMv13 budgets

## Certificate

- `selected_exponent_a`: ``
- `selected_exponent_b`: ``
- `selected_formula`: ``
- `canonical_formula`: `M^1 L^2`
- `canonical_gate`: `FAIL_NOT_ENOUGH_KNOTS`
- `certificate_status`: `FAIL_NOT_ENOUGH_KNOTS`
- `interpretation`: `Need at least three knots with valid BEMv13 budgets.`
- `n_targets_requested`: `3`
- `n_valid_budgets`: `0`
- `uses_observed_alpha`: `no`
- `next_gate`: `BEMv19_MULTI_KNOT_PRODUCTION_OR_Q_MINUS_2_SYMBOL_DERIVATION`

## Interpretation

If the status is `FAIL_NOT_ENOUGH_KNOTS`, run BEMv18 with at least three target knots. If the canonical candidate passes but is not best-score, this supports subleading behavior but does not uniquely identify b=2. If it is selected, that is strong empirical support for the q_{-2} route.

## Next gate

\[
\boxed{\text{BEMv19: multi-knot production grid or explicit }q_{-2}\text{ symbolic derivation.}}
\]