# Route B BEMv14 certified-length convergence
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


BEMv14 tests whether the certified-length budget remains stable under refinement suggested by BEMv12 isolated by BEMv10.

BEMv10 checks whether a BEMv9 finite-correction normalizer remains stable over a refinement grid.

BEMv9 computes:

\[
\Delta F_{\rm phys}^{(q)}=\Delta F_{\rm pair}/\mathcal N_q
\]

and

\[
\alpha^{-1}_{\rm pred,blind}^{(q)}
=
\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm long}
+
\Delta F_{\rm phys}^{(q)}\right].
\]

BEMv10 does not compare with observed alpha. It only checks stability.

## Outputs

```text
normalizer_convergence_grid.csv
normalizer_stability_summary.csv
alpha_budget_v10_convergence.csv
blind_alpha_convergence_v10.md
run_config_v10.json
runs/<run_id>/   # only when BEMv10 launches BEMv9 internally
```

## Reuse existing BEMv9 folders

```bash
python routeB_RT_bem_v14_certified_convergence.py \
  --from-bemv9-outdirs outputs_routeB_BEM_v9_fast \
  --outdir outputs_routeB_BEM_v10_from_v9
```

This produces a diagnostic report, but one folder is not enough to pass the full convergence gate.

## Fast internal grid

```bash
python routeB_RT_bem_v14_certified_convergence.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v10_fast \
  --n-center-list 8,10,12 \
  --n-theta-list 3,3,4 \
  --n-sphere-list 14,18,24 \
  --tube-fraction-list 0.38,0.32,0.28 \
  --outer-factor-list 2.2,2.6,3.0
```

## Larger paired grid

```bash
python routeB_RT_bem_v14_certified_convergence.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v10   --n-center-list 24,32,40,48   --n-theta-list 5,6,7,8   --n-sphere-list 96,144,196,256   --tube-fraction-list 0.35,0.30,0.25,0.20   --outer-factor-list 2.4,2.8,3.2,3.6   --length-samples 24000   --pair-fit-min-M 10
```

## Stability gate

A normalizer passes only if:

```text
n_runs >= min_grid_runs
pass_fraction = 1
alpha_inv_blind_cv_abs <= alpha_cv_threshold
abs_correction_ratio_max <= subleading_threshold
```

Defaults:

```text
min_grid_runs = 3
alpha_cv_threshold = 0.01
subleading_threshold = 0.05
```

This is not the derivation. It is the convergence gate for the BEMv9 normalizer.