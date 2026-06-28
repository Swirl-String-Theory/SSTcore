# Route B BEMv6 convergence-grid audit
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


BEMv6 wraps BEMv5 over a mesh/tube/outer-boundary grid.

BEMv5 computes one blind value:

\[
A=\alpha^{-1}_{\rm pred,blind}
=
\frac12(S_{\rm soft}+S_{\rm RT}^{\rm ren}).
\]

BEMv6 tests whether that value is stable under:

\[
h\to0,\qquad a\to0,\qquad R\to\infty.
\]

The continuum trend is fit as:

\[
A(h,a,R)=A_\infty+c_h h+c_a a+c_R R^{-1}+\cdots.
\]

## New BEMv6 outputs

```text
convergence_grid.csv
continuum_limit_fit.csv
blind_alpha_convergence.md
runs/<run_id>/...
```

Each `runs/<run_id>/` folder contains the full BEMv5 outputs:

```text
raw_spectrum_*.npy
cutoff_series.csv
renormalized_action_fit.csv
heat_kernel_counterterms.csv
soft_sector_index.csv
blind_alpha_prediction.md
```

## Fast run

```bash
python routeB_RT_bem_v6_convergence_grid.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v6_fast \
  --n-center-list 10,12,14 \
  --n-theta-list 3,4,4 \
  --n-sphere-list 18,24,32 \
  --tube-fraction-list 0.35,0.30,0.25 \
  --outer-factor-list 2.2,2.6,3.0
```

## Larger paired grid

```bash
python routeB_RT_bem_v6_convergence_grid.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v6 \
  --n-center-list 24,32,40,48 \
  --n-theta-list 5,6,7,8 \
  --n-sphere-list 96,144,196,256 \
  --tube-fraction-list 0.35,0.30,0.25,0.20 \
  --outer-factor-list 2.4,2.8,3.2,3.6 \
  --counterterm-fit-min-M 8 \
  --fit-min-M 8
```

## Cartesian grid

Warning: this can become expensive quickly.

```bash
python routeB_RT_bem_v6_convergence_grid.py \
  --ideal ideal.txt \
  --grid-mode cartesian \
  --n-center-list 24,32 \
  --n-theta-list 5,6 \
  --n-sphere-list 96,144 \
  --tube-fraction-list 0.30,0.25 \
  --outer-factor-list 2.8,3.2
```

## Interpretation

BEMv6 is still not an alpha derivation. It is the convergence falsifier. If the blind quantity does not stabilize under the grid, the current Route-B operator/normalization is not yet a source of \(\alpha\).
