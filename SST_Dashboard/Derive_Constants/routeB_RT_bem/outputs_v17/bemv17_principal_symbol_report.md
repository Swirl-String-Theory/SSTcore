# BEMv17 principal-symbol / heat-kernel report

This report is alpha-blind. It does not contain or compare against observed fine structure.

## Target

BEMv17 identifies the exact remaining proof obligation for

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]

The target is to derive the first surviving pair-subtracted residual symbol:

\[
q_{-2}(x,\xi).
\]

If the residual starts at order -2, then the length exponent is fixed:

\[
b=2.
\]

Mode extensivity fixes:

\[
a=1.
\]

Together:

\[
\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}
\]

## Certificate

- `normalizer`: `M_max L_cert^2`
- `normalizer_code`: `M_Lcert2`
- `bemv16_status`: `CONDITIONAL_HEAT_KERNEL_DTN_CERTIFICATE`
- `bemv17_status`: `PRINCIPAL_SYMBOL_PROOF_OBLIGATION_CERTIFICATE`
- `symbol_target`: `first surviving pair-subtracted residual q_{-2}`
- `mode_exponent_a`: `1`
- `length_exponent_b`: `2`
- `uses_observed_alpha`: `no`
- `stageD_alpha_inv_mean`: `137.15486676613227`
- `stageD_alpha_inv_cv_abs`: `5.894392513597222e-06`
- `stageCD_alpha_inv_mean`: `137.15528451885825`
- `stageCD_alpha_inv_cv_abs`: `1.1352779235901546e-05`
- `next_gate`: `BEMv18_MULTI_KNOT_LENGTH_EXPONENT_OR_SYMBOL_EXPANSION_Q_MINUS_2`

## Interpretation

BEMv17 is stronger than BEMv16 because it localizes the remaining mathematical burden: derive cancellation of the order 0 and order -1 residual terms, and show that the first nonzero pair-subtracted symbol is order -2.

## Next gate

\[
\boxed{\text{BEMv18: either multi-knot }b=2\text{ test or explicit }q_{-2}\text{ symbolic expansion.}}
\]