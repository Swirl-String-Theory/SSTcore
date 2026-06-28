# Route B BEMv16 heat-kernel normalizer
## Scale-role convention: \(r_c\), \(R_{\rm horn}\), and \(a_{\rm tube}\)

Route-B BEM is a **dimensionless certified-geometry programme**.  Its core
normalizer uses the certified ropelength coordinate \(L_{\rm cert}\), retained
mode count \(M_{\max}\), and pair correction \(\Delta F_{\rm pair}\).  It does
not require inserting a physical core radius into the numerical BEM score.

For physical interpretation, use the following scale separation:

\[
r_c \equiv R_{\rm horn}
\]

where \(R_{\rm horn}\) is the horn-torus / return-flow circulation radius.  Do
not silently identify \(r_c\) with the local ideal-tube radius.  Instead write

\[
a_{\rm tube}=\frac{R_{\rm horn}}{\chi_h}=\frac{r_c}{\chi_h},
\qquad
\ell_K^{\rm phys}=2a_{\rm tube}L_{\rm cert}.
\]

Thus the dimensionless Route-B normalizer remains

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2},
\]

while the physical reconstruction uses

\[
L_{\rm phys}^{2}
=
4a_{\rm tube}^{2}L_{\rm cert}^{2}
=
4\frac{r_c^2}{\chi_h^2}L_{\rm cert}^{2}.
\]

Only if \(\chi_h=\chi_h(K)\) is later made topology-dependent should a separate
horn-effective scan be introduced,

\[
\mathcal N_{\rm eff}
=
M_{\max}
\left(\frac{L_{\rm cert}}{\chi_h(K)}\right)^2 .
\]

Default BEM mode remains `certified`: do not replace \(L_{\rm cert}\) by a
horn-effective scale in BEMv1--BEMv19 results unless an explicit
`horn-effective` scan is being run.


BEMv16 is the analytic/proof-obligation step after BEMv15.

It does **not** run a new BEM solve and it does **not** use observed alpha.

It certifies the conditional normalizer:

\[
\boxed{
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
}
\]

## Run

```bash
python routeB_RT_bem_v16_heat_kernel_normalizer.py \
  --v15-outdir outputs_routeB_BEM_v15_normalizer_law \
  --outdir outputs_routeB_BEM_v16_heat_kernel
```

## Outputs

```text
bemv16_proof_obligations.csv
bemv16_scaling_law_table.csv
bemv16_normalizer_derivation.csv
bemv16_v15_numeric_link.csv
bemv16_heat_kernel_certificate.csv
bemv16_heat_kernel_appendix.tex
bemv16_heat_kernel_report.md
run_config_v16.json
```

## Status

BEMv16 proves the normalizer only conditionally:

1. R--T maps are first-order DtN/Steklov boundary operators.
2. The pair action is mode-extensive in \(M_{\max}\).
3. The residual finite density has second-order length covariance.

Under these assumptions:

\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

The next gate is BEMv17: derive the \(L_{\rm cert}^{2}\) covariance from the principal symbol / heat-kernel coefficients.
