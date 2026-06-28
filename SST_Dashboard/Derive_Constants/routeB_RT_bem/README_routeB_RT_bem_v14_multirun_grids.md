# BEMv14 multirun over multiple grids
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


Ja — dit is inderdaad nodig als je meer wilt dan één intra-grid check.

Een enkele BEMv14-run test alleen **stabiliteit binnen één grid-familie**.
De multirun-wrapper test vervolgens of **dezelfde normalizer en blind budget**
ook overeind blijven over meerdere onafhankelijke grid-families.

## Wat dit script doet

Het script `routeB_RT_bem_v14_multirun_grids.py`:

1. draait `routeB_RT_bem_v14_certified_convergence.py` meerdere keren;
2. elke keer met een andere grid-familie;
3. verzamelt per grid de gekozen normalizer;
4. maakt een cross-grid consensus-audit.

## Belangrijkste outputs

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`

## Quick multirun

```bash
python routeB_RT_bem_v14_multirun_grids.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v14_multirun   --suite-profile quick
```

## Standard multirun

```bash
python routeB_RT_bem_v14_multirun_grids.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v14_multirun_std   --suite-profile standard
```

## Reuse-mode

Als je al een BEMv13-outputmap hebt en eerst alleen de wrapper wilt testen:

```bash
python routeB_RT_bem_v14_multirun_grids.py   --from-bemv13-outdirs outputs_routeB_BEM_v13_certified   --outdir outputs_routeB_BEM_v14_multirun_reuse   --suite-profile quick
```

Je mag ook meerdere BEMv13-mappen meegeven, één per grid-familie:

```bash
python routeB_RT_bem_v14_multirun_grids.py   --from-bemv13-outdirs outdir1,outdir2,outdir3   --outdir outputs_routeB_BEM_v14_multirun_reuse   --suite-profile quick
```

## Wanneer is dit geslaagd?

Pas als:

1. per grid-familie een stabiele normalizer passeert;
2. dezelfde normalizer terugkomt over meerdere grids;
3. de cross-grid spreiding klein blijft.

Dus ja:

\[
\boxed{
\text{multirun over meerdere grids is de juiste volgende stap.}
}
\]

Maar ook dit blijft nog een **Route-B falsifier/provenance gate**, geen definitieve alpha-afleiding.