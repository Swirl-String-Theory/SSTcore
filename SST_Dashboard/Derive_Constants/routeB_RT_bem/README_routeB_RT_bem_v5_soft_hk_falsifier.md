# Route B BEMv5: soft-sector index + heat-kernel counterterms
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


BEMv5 extends BEMv4 by explicitly separating the candidate action into:

\[
S_{\rm total}=S_{\rm soft}+S_{\rm RT}^{\rm ren}.
\]

It still does **not** compare with CODATA alpha and does **not** fit alpha.

## Required outputs

BEMv5 writes:

```text
raw_spectrum_<knot>.npy
cutoff_series.csv
renormalized_action_fit.csv
heat_kernel_counterterms.csv
soft_sector_index.csv
blind_alpha_prediction.md
```

plus:

```text
raw_spectrum_manifest.csv
run_config.json
idealxml_sampled_ideal_used.txt
```

## New BEMv5 terms

The raw R--T spectral action is

\[
S_M(K)=-\sum_{j=1}^{M}\log\lambda_j(K),
\]

with vacuum subtraction

\[
\Delta S_M(K/0_1)=S_M(K)-S_M(0_1).
\]

BEMv5 adds heat-kernel-style counterterm fitting:

\[
\Delta S_M
=
S_{\rm RT}^{\rm ren}
+a_1M
+a_2M^{1/2}
+a_3\log M
+b_1M^{-1/2}
+b_2M^{-1}
+\cdots .
\]

The soft-sector term is explicit:

\[
S_{\rm soft}=N_{\rm soft}V_{\rm soft}.
\]

Default:

\[
N_{\rm soft}=4,\qquad V_{\rm soft}=\frac{4\pi}{3}.
\]

The blind working prediction is

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12\left(S_{\rm soft}+S_{\rm RT}^{\rm ren}\right).
\]

This is a Route-B working map, not yet a theorem.

## Fast run

```bash
python routeB_RT_bem_v5_soft_hk_falsifier.py \
  --ideal ideal.txt \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1 \
  --outdir outputs_routeB_BEM_v5_fast \
  --n-center 12 --n-theta 4 --n-sphere 32 \
  --fit-min-M 4 \
  --counterterm-fit-min-M 4
```

## More serious run

```bash
python routeB_RT_bem_v5_soft_hk_falsifier.py   --ideal ideal.txt   --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:1:2   --outdir outputs_routeB_BEM_v5   --n-center 48 --n-theta 8 --n-sphere 256   --fit-min-M 10   --counterterm-fit-min-M 10
```

## Try different soft-sector assumptions

No soft term:

```bash
python routeB_RT_bem_v5_soft_hk_falsifier.py --ideal ideal.txt --soft-volume-mode none
```

Explicit numeric soft volume:

```bash
python routeB_RT_bem_v5_soft_hk_falsifier.py \
  --ideal ideal.txt \
  --soft-volume-mode numeric \
  --soft-volume-value 4.1887902047863905
```

## Interpretation

BEMv5 is still a falsifier/provenance harness. A true alpha derivation requires:

1. a stable renormalized limit,
2. a stable soft-sector theorem,
3. mesh/tube/outer-boundary convergence,
4. only then blind comparison with observed fine structure.


## Unknot fallback

The correct Brian Gilbert file includes `0:1:1`. If a local copy starts at `3:1:1`, BEMv5 can still run controls by generating the analytic unit-circle unknot:

```bash
--auto-add-unknot
```

This is enabled by default. Disable it with:

```bash
--no-auto-add-unknot
```