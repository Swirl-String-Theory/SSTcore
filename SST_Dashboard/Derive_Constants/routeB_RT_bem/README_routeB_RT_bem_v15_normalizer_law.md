# Route B BEMv15 normalizer law
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


BEMv15 starts the analytic step after BEMv14.

BEMv14 showed, across multiple grid families, that the certified-length budget repeatedly selects:

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]

BEMv15 does **not** run a new BEM solve. It ingests Stage A/B/C/D results and writes a conditional normalizer-law certificate.

## Run on Stage A/B/C/D zips

```bash
python routeB_RT_bem_v15_normalizer_law.py \
  --inputs outputs_routeB_BEM_v14_stageABC.zip,outputs_routeB_BEM_v14_stageD.zip \
  --outdir outputs_routeB_BEM_v15_normalizer_law
```

## Outputs

```text
bemv15_stage_summary.csv
bemv15_consensus_summary.csv
bemv15_budget_points.csv
bemv15_exponent_scan.csv
bemv15_normalizer_law_certificate.csv
bemv15_normalizer_law_appendix.tex
bemv15_normalizer_law_report.md
run_config_v15.json
```

## Core statement

Under:

1. mode-extensivity of the truncated pair spectral action,
2. length-scale covariance of the finite R--T density,

the minimal separable monomial normalizer is:

\[
\boxed{
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
}
\]

## Important limitation

The exponent \(b=2\) cannot be learned from single-knot data alone because \(L_{\rm cert}(3_1)\) is fixed across the current grids. BEMv15 therefore marks the result as conditional.

The next gate should be a heat-kernel / DtN proof or a multi-knot certified-length test.
