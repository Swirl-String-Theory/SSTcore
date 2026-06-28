# BEMv19 link geometry parser
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


BEMv19 voegt de aparte multi-component parser toe voor links.

Doel: deze link-ID’s kunnen nu als geometry records worden meegenomen:

```text
L2a1
L4a1
L5a1
L6a1
L8a1
L6a4
L6n1
```

De huidige BEMv8/BEMv13/BEMv18 pipeline is nog single-component. BEMv19 draait daarom nog geen definitieve R--T determinant voor links, maar maakt de geometry-laag klaar.

## Run

```bash
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v19_links \
  --links L2a1,L4a1,L5a1,L6a1,L8a1,L6a4,L6n1
```

## Alle links uit ideal.txt pakken

```bash
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v19_all_links \
  --include-all-links
```

## Outputs

```text
link_record_catalog.csv
link_component_catalog.csv
link_geometry_summary.csv
link_pair_distances.csv
link_gauss_linking_matrix.csv
link_missing_catalog.csv
link_parser_certificate.csv
link_routeB_integration_plan.md
link_multicomponent_appendix.tex
run_config_v19.json
```

## Wat wordt berekend?

Per link:

- aantal componenten;
- Fourier-coefficients per component;
- numerieke arclength per component;
- totale component-lengte;
- minimumafstand tussen componenten;
- Gauss linking integral per componentpaar;
- afgeronde linking estimate.

## Status

\[
\boxed{
\text{BEMv19: link geometry parser ready; block R--T operator open.}
}
\]

## Volgende stap

BEMv20 moet de single-component boundary map vervangen door een block operator:

\[
\Lambda^{\rm link}_{R/T}
=
(\Lambda^{R/T}_{ab})_{a,b=1}^{m}.
\]

Dan kunnen links echt in dezelfde Route-B spectral determinant komen.
