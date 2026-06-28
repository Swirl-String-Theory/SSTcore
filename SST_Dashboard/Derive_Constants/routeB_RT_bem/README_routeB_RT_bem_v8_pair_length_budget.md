# Route B BEMv8 pair-subtracted length budget
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


BEMv8 fixes the two main BEMv7 pathologies:

1. **Absolute longitudinal scale is restored.**  
   The large term uses alpha-blind raw Fourier arclength from `ideal.txt`, not unit-arclength normalized BEM geometry.

2. **Finite R--T correction is pair-subtracted directly.**  
   BEMv8 fits \(S_M(K)-S_M(0_1)\) in one fit instead of subtracting two large fitted constants.

The working blind budget is:

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12\left[
N_{\rm soft}V_{\rm soft}L_{\rm long}(3_1)
+
\Delta F_{\rm pair}(3_1/0_1)
\right].
\]

Default:

\[
N_{\rm soft}=4,
\qquad
V_{\rm soft}=4\pi/3.
\]

No observed alpha is used.

## Outputs

```text
geometric_length_audit.csv
hk_length_coefficients_phys.csv
spectral_length_estimate_phys.csv
pair_subtracted_correction.csv
alpha_component_budget_v8.csv
blind_alpha_prediction_v8.md
run_config_v8.json
```

BEMv8 also writes/reuses a `bemv5_base/` folder with raw spectra.

## Fast run

```bash
python routeB_RT_bem_v8_pair_length_budget.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v8_fast \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1 \
  --n-center 12 --n-theta 4 --n-sphere 32 \
  --length-samples 12000 \
  --pair-fit-min-M 4
```

## More serious run

```bash
python routeB_RT_bem_v8_pair_length_budget.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v8 \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:1:2 \
  --n-center 48 --n-theta 8 --n-sphere 256 \
  --length-samples 24000 \
  --pair-fit-min-M 10
```

## Reuse an existing BEMv5 output folder

```bash
python routeB_RT_bem_v8_pair_length_budget.py \
  --from-bemv5-outdir outputs_routeB_BEM_v5_fast \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v8_from_v5
```

## Important modes

Default length branch:

```bash
--length-source geometric_raw
```

Diagnostic spectral branch:

```bash
--length-source spectral_norm
```

The `geometric_raw` branch is alpha-blind because it computes arclength directly from Fourier coefficients. It does not read or use observed alpha.

## Interpretation

BEMv8 is still not a final derivation. It is the corrected component-budget falsifier. The next gate is convergence under mesh/tube/outer-boundary refinement.
