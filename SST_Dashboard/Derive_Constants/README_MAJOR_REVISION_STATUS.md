## Major-revision claim-status correction

The current safe presentation after the external review is:

```text
The package derives a conditional finite-cell fine-structure-scale certificate.
It does not yet derive the QED fine-structure constant from first principles.
```

Use the following hierarchy.

### Safe derived statements

\[
N_p=4
\]

is derived in the spherical finite-cell surface/perimeter class.  This is
supported by the surface spectrum \(k_\ell=(\ell-1)(\ell+2)\), perturbative
finite-core gap checks, nonlinear star-shaped tests through \(\ell_{\max}=6\),
and the Euclidean isoperimetric inequality for finite-perimeter cells.

\[
\chi_R=2
\]

is derived **within the minimal reciprocal pressure action**, using the
Laplace-matched pressure identity, but only after excluding same-order
nonreciprocal terms such as \(\chi_R^2\), \(\chi_R^{-2}\), and \(\log\chi_R\).

\[
q_\phi=1,\qquad \Lambda_\phi=4\pi R\mathcal K_{\rm cell}
\]

are derived from exterior Hodge/capacity theory.

\[
\Lambda_\phi=\frac{E_{\rm eff}}{2}
\]

is derived inside the canonical linearized phase--pressure normal-mode
reduction, provided \(E_{\rm eff}\) is identified with the cycle-averaged
quadratic energy of the same interior mode family.

### Conditional or open gates

The pressure prefactor

\[
\frac{16\pi}{3}=N_p\frac{4\pi}{3}
\]

is **not fully derived**.  \(N_p=4\) is derived, but the sector-volume
normalization \(4\pi/3\) per pressure sector per unit ropelength remains a
blocking coefficient.

The correction

\[
\frac{11}{48}
\]

is conditional on \(w_\perp=1\).  The derived structure is

\[
\sigma=3+\frac23w_\perp.
\]

The current relaxed GP-core proxy gives

\[
w_\perp\simeq2.076,
\]

so \(w_\perp=1\) is an open primitive-equation gate, not a solved result.

The retrospective number

\[
\alpha_{\rm cell}^{-1}=137.035999211
\]

is a calibrated consistency check because it uses the inserted
\(E_0=274.074996\).  Do not present it as a prediction.

The safer non-CODATA numerical certificate is

\[
\alpha_{\rm cell}^{-1}=137.035953(28),
\]

from the BEM/NLS finite-cell calculation, and even this remains conditional on
the model-dependent coefficient gates above.

The parameter-light headline is

\[
\frac{8\pi}{3}\mathcal L_{3_1}=137.1547,
\]

which is within \(8.7\times10^{-4}\) of CODATA before precision corrections.

### Recommended wording

Use:

```text
fine-structure-scale finite-cell certificate
```

or

```text
dimensionless cell eigenvalue numerically close to alpha
```

unless the two-cell far-field theorem

\[
V(r)=\alpha_{\rm cell}\frac{\hbar c}{r}+O(r^{-2})
\]

is proved.

Avoid:

```text
first-principles derivation of QED alpha
```

until the \(4\pi/3\) sector-volume gate, the \(w_\perp=1\) gate, and the
far-field interaction theorem are closed.
