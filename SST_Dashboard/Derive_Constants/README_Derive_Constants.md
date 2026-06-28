# Derive_Constants package

This package contains the four-paper derivation/closure chain for the finite-cell
constant derivation program, together with the Python gate-auditors and their
CSV/Markdown outputs.

The package is deliberately organized as a **claim-status hierarchy**.  It does
not claim that every result is a primitive derivation from first principles.
Each coefficient is tagged by the strongest status currently justified by the
manuscripts and the reproducibility scripts.

## Directory layout

```text
Derive_Constants/
├── Manuscripts/
│   ├── 1_SST_constants_derivation_v8_paper1_derived_gate_model_answers.tex
│   ├── 2_followup_spherical_cell_derivation_paper2_NLS_with_appendix_model_answers.tex
│   ├── 3_BEM_NLS_Finite_Cell_Eigenvalue_FarField_with_appendix_model_answers.tex
│   └── 4_Uniqueness_Minimal_Finite_Cell_Variational_Reduction.tex
└── code/
    ├── *.py
    ├── outputs_*/
    └── DERIVED_GATE_EVIDENCE_MANIFEST.json
```

All manuscript references to scripts assume the relative path

```text
../code/
```

from inside the `Manuscripts/` directory.

## The four papers

### Paper I — closure ledger and algebraic core

Paper I records what the Compton-core scaling model fixes algebraically and what
requires additional dynamics.  It is the status ledger for the full package.  It
now records:

- \(N_p=4\) derived in the spherical surface spectrum, with perturbative,
  nonlinear star-shaped, and finite-perimeter global-topology stability checks.
- \(A_\chi=\chi_R+N_p/\chi_R\) and \(\chi_R=2\) derived in the
  Laplace-matched reciprocal pressure model.
- \(11/48\) derived inside the unweighted isotropic GP/NLS shell reduction.
- \(q_\phi=1\) and the exterior capacity relation derived by Hodge theory.
- \(\Lambda_\phi=E_{\rm eff}/2\) derived inside the canonical linearized
  phase--pressure normal-mode reduction.
- The remaining primitive gate: \(w_\perp=1\) from the full GP/SST core-profile
  reduction.

### Paper II — spherical pressure-cell / NLS-shell derivation

Paper II develops the spherical finite-cell pressure functional and the NLS shell
coefficient chain.  It should be read with Paper IV for the upgraded status of
\(N_p=4\), \(\chi_R=2\), and \(\Lambda_\phi=E_{\rm eff}/2\).

Main status:

```text
11/48 is derived within the unweighted isotropic GP/NLS shell reduction.
```

The remaining primitive task is to derive the unweighted transverse
normalization \(w_\perp=1\) from the full GP/SST core-profile dynamics rather
than from shell normalization.

### Paper III — BEM/NLS finite-cell eigenvalue and far-field certificate

Paper III is the numerical finite-cell paper.  It tests the BEM/NLS stationary
point and the far-field implementation.

Main status:

```text
E_star is pressure-selected by the NLS shell action.
The far-field normalization is derived inside the finite-cell normal-mode
reduction, conditional on identifying E_eff with the same canonical interior
mode-family energy.
```

The paper should not be presented as an unconstrained derivation of QED
\(\alpha\).  It is a conditional finite-cell derivation/certificate inside the
stated reduction.

### Paper IV — gate derivations and uniqueness/minimality

Paper IV is the theorem-style companion paper.  It contains the most compact
statement of the current derivation status:

- Theorem 1/1b/1c/1d: \(N_p=4\) from pressure constraints, surface spectrum,
  perturbative/nonlinear shape stability, and global isoperimetry.
- Theorem 2: \(11/48\) within unweighted isotropic GP/NLS shell normalization.
- Theorem 3: \(\chi_R=2\) from Laplace-matched pressure self-duality.
- Theorem 4/4b: \(q_\phi=1\), exterior capacity, and
  \(\Lambda_\phi=E_{\rm eff}/2\) within canonical phase--pressure normal modes.

## Recommended execution order

Run scripts from the `code/` directory.

### 1. Pressure-sector count \(N_p=4\)

```bash
python derive_pressure_mode_cutoff_surface_spectrum.py --outdir outputs_surface_mode_cutoff
```

Expected status:

```text
DERIVED_IN_SPHERICAL_SURFACE_VARIATION
```

Robustness checks:

```bash
python test_finite_core_nonspherical_shape_corrections.py --outdir outputs_finite_core_shape
python solve_nonlinear_shape_stability.py --lmax 6 --samples 300 --opt-starts 20 --opt-start-amplitude 1.0 --maxiter 400 --outdir outputs_nonlinear_shape_stability_lmax6_opt
```

Expected status:

```text
PASS_NO_LEADING_PROMOTION
PASS_NONLINEAR_SHAPE_STABILITY_IN_STAR_SHAPED_CLASS
```

Interpretation: \(\ell\ge2\) modes remain higher-order shape corrections; the
leading pressure manifold remains
\(\mathcal H_0\oplus\mathcal H_1\), so \(N_p=1+3=4\).

### 2. Radius action and \(\chi_R=2\)

```bash
python derive_pressure_self_duality_from_laplace_matching.py --outdir outputs_laplace_self_duality
```

Expected result:

```text
P_kinetic = P_Laplace
chi_R = sqrt(N_p) = 2
```

Interpretation: \(A_\chi=\chi_R+N_p/\chi_R\) is derived within the
Laplace-matched reciprocal pressure model.

### 3. GP/NLS shell coefficient \(11/48\)

```bash
python derive_gp_core_profile_second_variation.py --outdir outputs_gp_core_profile_second_variation
```

Expected result for the canonical unweighted isotropic shell:

```text
sigma = 11/3
c2 = 11/48
```

Important sensitivity runs:

```bash
python derive_gp_core_profile_second_variation.py --weight-mode profile_radial_ratio --outdir outputs_gp_core_profile_radial_ratio
python derive_gp_core_profile_second_variation.py --weight-mode profile_energy_ratio --outdir outputs_gp_core_profile_energy_ratio
```

Interpretation: \(11/48\) is derived within the unweighted isotropic GP/NLS shell
reduction.  The primitive gate \(w_\perp=1\) is not yet derived from the full
GP/SST core-profile dynamics.

Optional next-step auditors for \(w_\perp\):

```bash
python derive_relaxed_gp_core_hessian_wperp.py --outdir outputs_relaxed_gp_wperp
python derive_full_gp_field_schur_wperp.py --outdir outputs_full_gp_schur_wperp
```

These currently serve as falsifiable gate-auditors rather than completed
derivations.

### 4. Exterior Hodge capacity and \(q_\phi=1\)

```bash
python solve_one_cell_hodge_phase_hessian.py --outdir outputs_hodge_phase_hessian
```

Expected result:

```text
q_phi = 1
Lambda_phi = 4*pi*R*K_cell
```

### 5. Interior phase-Hessian chain

First, radial phase-Hessian budget:

```bash
python solve_interior_one_cell_phase_hessian.py --outdir outputs_interior_phase_hessian
python derive_phase_hessian_density_budget.py --outdir outputs_phase_hessian_density_budget
python derive_phase_budget_closure_attempt.py --outdir outputs_phase_budget_closure
python derive_accessible_area_phase_budget_gate.py --outdir outputs_accessible_area_budget
```

Then the final normal-mode half-budget identity:

```bash
python derive_phase_pressure_exchange_self_duality.py --outdir outputs_phase_pressure_self_duality
```

Expected result:

```text
PHASE_PRESSURE_HALF_BUDGET_DERIVED_WITHIN_CANONICAL_NORMAL_MODE_REDUCTION
Lambda_phi/(E_eff/2) = 1
```

Interpretation: \(\Lambda_\phi=E_{\rm eff}/2\) is derived within the canonical
linearized phase--pressure normal-mode reduction, combined with the radial
optimum and accessible-area projection.  The remaining physical bridge is to
identify the \(E_{\rm eff}\) used in the pressure-cell chain with the
cycle-averaged quadratic energy of that same canonical interior mode family.

## Current final claim-status

### Derived within the stated reductions

\[
N_p=4.
\]

\[
A_\chi=\chi_R+\frac{N_p}{\chi_R},\qquad \chi_R=2.
\]

\[
q_\phi=1,\qquad \Lambda_\phi=4\pi R\mathcal K_{\rm cell}.
\]

\[
\Lambda_\phi=\frac{E_{\rm eff}}{2}
\quad
\text{within canonical linearized phase--pressure normal modes}.
\]

\[
\mathcal K_{\rm cell}=\frac{E_{\rm eff}}{8\pi}
\quad (R=1).
\]

### Derived with a named normalization gate

\[
\frac{11}{48}
\quad
\text{within the unweighted isotropic GP/NLS shell reduction}.
\]

### Still open at primitive-equation level

\[
w_\perp=1
\]

from the full GP/SST core-profile reduction.

Also still to be stated as a bridge assumption unless independently proven:

```text
E_eff is the cycle-averaged quadratic energy of the same canonical interior
mode family used in the phase--pressure normal-mode reduction.
```

## Minimal publishable wording

Use this wording when describing the full package:

```text
The fine-structure-scale coefficient is derived within the stated finite-cell
surface-spectrum, Laplace-matched pressure, unweighted GP/NLS shell, and
canonical phase--pressure normal-mode reductions.  The remaining primitive
task is to derive the transverse normalization w_perp=1 from the full GP/SST
core-profile dynamics and to justify the identification of E_eff with the same
canonical interior mode-family energy.
```

Do not state:

```text
alpha is derived from QED first principles.
```

Do state:

```text
alpha_cell is derived within the specified finite-cell reduction, subject to the
explicit remaining primitive normalization gate.
```

## Notes for running on Windows

Use PowerShell from the `code` directory:

```powershell
cd .\code
python .\derive_pressure_mode_cutoff_surface_spectrum.py --outdir outputs_surface_mode_cutoff
python .\derive_phase_pressure_exchange_self_duality.py --outdir outputs_phase_pressure_self_duality
```

For SciPy 1.17+, use the patched `solve_nonlinear_shape_stability.py` included
in this package; it uses `scipy.special.sph_harm_y` instead of the removed
`scipy.special.sph_harm`.

## Files added in this update

This update adds the phase--pressure normal-mode gate:

```text
code/derive_phase_pressure_exchange_self_duality.py
code/outputs_phase_pressure_self_duality/
```

and patches all four manuscripts so that \(\Lambda_\phi=E_{\rm eff}/2\) is no
longer listed as fully open.  It is now classified as derived inside the
canonical normal-mode reduction, with the physical \(E_{\rm eff}\)-identification
bridge stated explicitly.


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
