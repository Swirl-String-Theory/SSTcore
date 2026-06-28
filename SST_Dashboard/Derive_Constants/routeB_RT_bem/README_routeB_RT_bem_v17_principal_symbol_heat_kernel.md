# Route B BEMv17 principal-symbol / heat-kernel audit
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


BEMv17 sharpens the BEMv16 conditional certificate.

BEMv16 said:

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}
\]

provided mode-extensivity and second-order length covariance hold.

BEMv17 identifies the exact principal-symbol obligation:

\[
\sigma\!\left[\log(\Lambda_R\Lambda_T^{-1})\right]
=
q_{-2}(x,\xi)
+
q_{-3}(x,\xi)+\cdots
\]

after soft-sector removal and pair subtraction.

If the first surviving residual is \(q_{-2}\), then:

\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

## Run

```bash
python routeB_RT_bem_v17_principal_symbol_heat_kernel.py \
  --v16-outdir outputs_routeB_BEM_v16_heat_kernel \
  --outdir outputs_routeB_BEM_v17_principal_symbol
```

## Outputs

```text
bemv17_symbol_hierarchy.csv
bemv17_heat_kernel_coefficients.csv
bemv17_exponent_uniqueness.csv
bemv17_proof_gap_register.csv
bemv17_principal_symbol_certificate.csv
bemv17_principal_symbol_appendix.tex
bemv17_principal_symbol_report.md
run_config_v17.json
```

## Status

BEMv17 is still conditional. It does not derive alpha.

It says the next exact mathematical target is:

\[
\boxed{
q_{-2}(x,\xi)
}
\]

as the first surviving pair-subtracted R--T residual symbol.
