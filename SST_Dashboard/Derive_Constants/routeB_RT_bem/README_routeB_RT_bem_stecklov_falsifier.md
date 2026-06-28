# Route B v2: R--T BEM/Steklov falsifier
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


This is BEM v3 plus direct loading of ideal-knot Fourier data from the installed `SSTcore` package.

It keeps the BEM v3 backend:

\[
S_{ij}=\sqrt{A_i}\,G(x_i,x_j)\sqrt{A_j},
\]

parallel-transport tube frames, and screened self-patch terms.

## Install SSTcore

```bash
pip install SSTcore
```

## List available ideal.txt blocks

```bash
python routeB_RT_bem_stecklov_falsifier.py --source sstcore --list-sstcore-knots --sstcore-max-knots 50
```

## Run default controls from SSTcore

This loads:

```text
0:1:1, 3:1:1, 4:1:1
```

from `SSTcore.get_ideal_txt_path()`.

```bash
python routeB_RT_bem_stecklov_falsifier.py --source sstcore --outdir outputs_routeB_SSTcore
```

## Run multiple knots from SSTcore

```bash
python routeB_RT_bem_stecklov_falsifier.py \
  --source sstcore \
  --sstcore-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:2:1,6:1:1,6:2:1,6:3:1 \
  --outdir outputs_routeB_SSTcore_many
```

## Run all first N single-component ideal blocks

```bash
python routeB_RT_bem_stecklov_falsifier.py   --source file --ideal ideal.txt    --sstcore-knot-ids all   --sstcore-max-knots 20   --outdir outputs_routeB_SSTcore_all20
```

## Use a local coordinate ideal.txt instead

```bash
python routeB_RT_bem_stecklov_falsifier.py --source file --ideal ideal.txt --outdir outputs_routeB_file
```

## Output

When using SSTcore, the script writes the sampled coordinates it actually used to:

```text
<outdir>/sstcore_sampled_ideal_used.txt
```

This lets you reproduce the exact sampled input without relying on import state.

## Reminder

Passing all gates does not derive alpha. It only means this Route-B BEM v3.1 candidate survives the chosen falsifiers. A theorem-level map

\[
\alpha^{-1}=F(S_{RT}(3_1))
\]

must still be specified before any comparison with CODATA.