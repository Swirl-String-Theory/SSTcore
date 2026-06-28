# BEMv14 extensive multigrid suite
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


Dit pakket is de uitgebreide variant van de BEMv14 multirun-audit.

Doel:

\[
\boxed{
\text{test of }M_{\max}L_{\rm cert}^{2}
\text{ stabiel blijft over meerdere onafhankelijke grid-families.}
}
\]

Een enkele BEMv14-run test alleen intra-grid stabiliteit. Deze suite test ook cross-grid stabiliteit.

## Bestanden

```text
BEMv14_suite_stageA_probe.json
BEMv14_suite_stageB_production.json
BEMv14_suite_stageC_stress.json
BEMv14_suite_stageD_maximal.json
BEMv14_suite_all_stages_ABCD.json
run_bemv14_extensive_ABC.sh
run_bemv14_extensive_ABC.ps1
run_bemv14_stageD_maximal.sh
```

## Stage A — probe

Snelle check met kleine grids. Gebruik dit om te zien of alles technisch draait.

```bash
python routeB_RT_bem_v14_multirun_grids.py --ideal ideal.txt --outdir outputs_routeB_BEM_v14_stageA --grid-suite-json BEMv14_suite_stageA_probe.json
```

## Stage B — production

Meer serieuze grid-families: paired coarse, paired medium, cartesian mesh cross-check, outer-radius sweep, tube-radius sweep.

```bash
python routeB_RT_bem_v14_multirun_grids.py --ideal ideal.txt --outdir outputs_routeB_BEM_v14_stageB --grid-suite-json BEMv14_suite_stageB_production.json --length-samples 16000
```

## Stage C — stress

Fine paired grids, alternate tail fit, cartesian fine, tube-only and sphere-only boundary subspaces.

```bash
python routeB_RT_bem_v14_multirun_grids.py --ideal ideal.txt --outdir outputs_routeB_BEM_v14_stageC --grid-suite-json BEMv14_suite_stageC_stress.json
```

## Stage D — maximal

Alleen draaien als A/B/C intern consistent zijn. Deze is zwaar.

```bash
python routeB_RT_bem_v14_multirun_grids.py --ideal ideal.txt --outdir outputs_routeB_BEM_v14_stageD --grid-suite-json BEMv14_suite_stageD_maximal.json --subrun-timeout 7200 --grid-run-timeout 9000 --multirun-timeout 86400
```

## Run alles A/B/C

Linux/macOS/Git Bash:

```bash
./run_bemv14_extensive_ABC.sh ideal.txt outputs_routeB_BEM_v14_multirun_extensive
```

Windows PowerShell:

```powershell
.\run_bemv14_extensive_ABC.ps1 -Ideal ideal.txt -OutRoot outputs_routeB_BEM_v14_multirun_extensive
```

## Interpretatie

Een echte positieve uitkomst vereist:

1. per grid-familie `PASS_CERTIFIED_STABLE_NORMALIZER`;
2. dezelfde selected normalizer, liefst `M_Lcert2`;
3. cross-grid `PASS_CROSS_GRID_CONSENSUS`;
4. kleine aggregate CV;
5. correction blijft subleading.

Als meerdere normalizers passeren, is dat geen probleem maar wel een open theoretische vraag: dan moet BEMv15 de analytic justification van de normalizer leveren.