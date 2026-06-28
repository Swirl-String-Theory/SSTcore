# Route B BEMv4 zeta/cutoff falsifier
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


BEMv4 extends BEMv3.3 by saving raw spectra and building a cutoff-renormalized spectral-action audit.

## New required outputs

Each run writes:

```text
raw_spectrum_<knot>.npy
cutoff_series.csv
renormalized_action_fit.csv
blind_alpha_prediction.md
```

It also writes:

```text
raw_spectrum_manifest.csv
run_config.json
idealxml_sampled_ideal_used.txt
```

when applicable.

## Mathematical object

For each knot \(K\), BEMv4 computes generalized R--T impedance eigenvalues:

\[
\Lambda_R v=\lambda \Lambda_T v.
\]

The raw spectral action at cutoff \(M\) is

\[
S_M(K)=-\sum_{j=1}^{M}\log \lambda_j(K).
\]

Using the unknot as vacuum subtraction,

\[
\Delta S_M(K/0_1)=S_M(K)-S_M(0_1).
\]

The cutoff tail is fit to

\[
\Delta S_M
=
S_\infty
+
c_1M^{-1/2}
+
c_2M^{-1}
+
c_3M^{-3/2}.
\]

The blind Route-B working prediction is then printed as

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12 S_\infty.
\]

No CODATA alpha appears in the script or output.

## List available blocks

```bash
python routeB_RT_bem_v4_zeta_falsifier.py \
  --ideal ideal.txt \
  --list-ideal-xml-knots \
  --max-list 40
```

## Fast run on controls

```bash
python routeB_RT_bem_v4_zeta_falsifier.py \
  --ideal ideal.txt \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1 \
  --outdir outputs_routeB_BEM_v4_fast \
  --n-center 12 --n-theta 4 --n-sphere 32 \
  --fit-min-M 4
```

## More serious run

```bash
python routeB_RT_bem_v4_zeta_falsifier.py \
  --ideal ideal.txt \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:1:2 \
  --outdir outputs_routeB_BEM_v4 \
  --n-center 48 --n-theta 8 --n-sphere 256 \
  --fit-min-M 10
```

## First N single-component blocks

```bash
python routeB_RT_bem_v4_zeta_falsifier.py \
  --ideal ideal.txt \
  --ideal-xml-knot-ids all \
  --max-knots 20 \
  --outdir outputs_routeB_BEM_v4_all20
```

## Interpretation

Passing this audit does not derive alpha. It only gives a blind candidate number from the current R--T spectral-action hypothesis. A true derivation still requires:

1. stable mode-cutoff limit,
2. stable mesh/tube/outer-boundary limits,
3. canonical theorem-level map \(\alpha^{-1}=F(S_{RT}^{\rm ren})\),
4. only then comparison against observed alpha.
