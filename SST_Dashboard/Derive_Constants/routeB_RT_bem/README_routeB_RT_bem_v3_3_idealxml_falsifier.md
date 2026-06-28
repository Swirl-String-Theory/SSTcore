# Route B BEM v3.3 — Brian Gilbert `ideal.txt` compatible
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


This is the Route-B BEM/Steklov falsifier updated for the **correct Brian Gilbert ideal-knot database** that includes `0:1:1` unknot control plus single-component knots and multi-component links.

## What v3.3 fixes

v3.2 could read XML/Fourier `<AB>` blocks, but multi-component link blocks such as `0:1:2` and `2:2:1` contain nested `<Component>` sections. v3.3 now treats those correctly:

- single-component blocks are supported;
- multi-component blocks are listed but skipped by `--ideal-xml-knot-ids all`;
- if a multi-component block is selected explicitly, the script raises a clear error instead of collapsing components into one false centerline.

The BEM operator is unchanged:

```tex
S_{ij}=\sqrt{A_i}\,G(x_i,x_j)\sqrt{A_j}
```

with

```tex
G_R(r)=\frac{1}{4\pi r},
\qquad
G_T(r)=\frac{e^{-\mu r}}{4\pi r},
```

and generalized R--T spectrum

```tex
\Lambda_R v=\lambda\Lambda_T v.
```

## List supported blocks

```bash
python routeB_RT_bem_v3_3_idealxml_falsifier.py \
  --source file \
  --ideal ideal.txt \
  --list-ideal-xml-knots \
  --sstcore-max-knots 30
```

The output labels single-component entries as `single` and multi-component entries as `skip_n=2`, etc.

## Default control run

The correct file contains `0:1:1`, so the default control gate G6 now works:

```bash
python routeB_RT_bem_v3_3_idealxml_falsifier.py \
  --source file \
  --ideal ideal.txt \
  --outdir outputs_routeB_correct_ideal
```

## Fast test

```bash
python routeB_RT_bem_v3_3_idealxml_falsifier.py \
  --source file \
  --ideal ideal.txt \
  --outdir outputs_routeB_correct_ideal_fast \
  --n-center 10 --n-theta 3 --n-sphere 18 --modes 6 \
  --center-resolution-list 8,10,12 \
  --n-invariance-trials 1
```

## First 10 supported single-component blocks

```bash
python routeB_RT_bem_v3_3_idealxml_falsifier.py   --source file   --ideal ideal.txt   --ideal-xml-knot-ids all   --sstcore-max-knots 10   --outdir outputs_routeB_correct_ideal_all10
```

## Provenance

For every XML/Fourier run, the script writes the sampled coordinates actually used by BEM to:

```text
<outdir>/idealxml_sampled_ideal_used.txt
```

## Status

This remains a falsifier harness, not an alpha derivation. Passing the gates only means the proposed Route-B boundary operator survives the selected numerical tests.