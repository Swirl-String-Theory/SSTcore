# Route B BEMv18 multi-knot exponent test
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


BEMv18 tests the BEMv17 claim that the residual length exponent is:

\[
b=2.
\]

If the first surviving pair-subtracted R--T residual is \(q_{-2}\), the correction should be:

\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

BEMv18 checks this across multiple knots with different certified lengths.

## Dry-run plan

```bash
python routeB_RT_bem_v18_multiknot_exponent_test.py  --ideal ideal.txt  --targets-json BEMv18_targets_minimal.json  --outdir outputs_routeB_BEM_v18_plan  --dry-run-plan
```

## Lightweight internal BEMv13 smoke test

```bash
python routeB_RT_bem_v18_multiknot_exponent_test.py  --ideal ideal.txt  --targets 3:1:1,4:1:1,5:1:1  --outdir outputs_routeB_BEM_v18_smoke  --run-bemv13  --n-center 8  --n-theta 3  --n-sphere 14  --tube-fraction 0.34  --outer-factor 2.4
```

## Production target set

```bash
python routeB_RT_bem_v18_multiknot_exponent_test.py  --ideal ideal.txt  --targets-json BEMv18_targets_production.json  --outdir outputs_routeB_BEM_v18_production  --run-bemv13  --n-center 24  --n-theta 5  --n-sphere 96  --tube-fraction 0.30  --outer-factor 3.0  --pair-fit-min-M 8
```

## Reuse BEMv13 outputs

```bash
python routeB_RT_bem_v18_multiknot_exponent_test.py  --from-bemv13-outdirs out_3_1,out_4_1,out_5_1  --outdir outputs_routeB_BEM_v18_reuse
```

## Outputs

```text
bemv18_target_catalog.csv
bemv18_run_manifest.csv
bemv18_raw_multiknot_budget.csv
bemv18_length_exponent_scan.csv
bemv18_exponent_certificate.csv
bemv18_multiknot_appendix.tex
bemv18_multiknot_report.md
run_config_v18.json
```

## Interpretation

Strong result:

```text
certificate_status = PASS_CANONICAL_B2_SELECTED
```

Useful but weaker result:

```text
PASS_CANONICAL_SUBLEADING_BUT_NOT_BEST_SCORE
```

Failure / insufficient:

```text
FAIL_NOT_ENOUGH_KNOTS
```

This remains a falsifier/provenance test, not a final alpha derivation.