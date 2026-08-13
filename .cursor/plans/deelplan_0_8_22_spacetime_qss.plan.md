---
name: Deelplan 0.8.22 Spacetime QSS
overview: "Bump beide naar 0.8.22. Operational spacetime helpers + QSS eigenproblem/pseudospectrum scaffolding (ConditionalBridge; geen closed physics)."
todos:
  - id: d822-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d822-version-bump
    content: "Bump beide → 0.8.22"
    status: pending
  - id: d822-spacetime
    content: "Operational interval / radar / Lorentz-map helpers module"
    status: pending
  - id: d822-qss
    content: "QSS scaffolding op synthetische matrices + epistemic status labels"
    status: pending
  - id: d822-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d822-new-tests
    content: "CI stap 4–5: nieuwe tests + 100%"
    status: pending
  - id: d822-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.22: operational spacetime and QSS scaffolding"
    status: pending
isProject: false
---

# Deelplan 0.8.22 — Operational spacetime + QSS

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_21_certification_biot.plan.md](deelplan_0_8_21_certification_biot.plan.md)  
**Next:** [deelplan_0_8_23_provenance.plan.md](deelplan_0_8_23_provenance.plan.md)  
**Target:** beide **"0.8.22"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — **geen `CheckKind` type** tot 0.8.27; gebruik `std::string epistemic_status` met exportstrings.

## Must-ship

```text
include/sst_operational_spacetime.h
src/operational_spacetime.{cpp,_py,_node}.cpp
include/sst_qss_spectroscopy.h
src/qss_spectroscopy.{cpp,_py,_node}.cpp
tests/test_operational_spacetime.py
tests/test_qss_spectroscopy.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.22/`
- `SST-CANON/been_processed/sources/v0.8.22_operational_spacetime_qss/`

## CI-poort


1. Baseline Python/Node/parity groen.
2. Operationele helpers en QSS-productiecode toevoegen, nog zonder nieuwe tests.
3. Regressie: bestaande suite 100% groen.
4. Nieuwe analytische, synthetische, foutpad- en paritytests.
5. Final: docs, statuslabels, bindings en versies volledig bijgewerkt.

## Scope


- Version bump → `0.8.22`.
- Nieuwe module(s), bijvoorbeeld `src/operational_spacetime.*` en `src/qss_spectroscopy.*`.
- Lorentz-map / proper-time rate scaffolding met numerieke residuals.
- QSS: eigenproblem en pseudospectrum op **synthetische** testmatrices.
- Statusstrings (tot 0.8.27): `CONDITIONAL_BRIDGE`, `OPEN_RESEARCH_GATE`, `SYNTHETIC_DIAGNOSTIC` — zie SHARED_CONVENTIONS. Expliciet in API-docstrings.

**Radarconstructie**

```cpp
struct RadarInterval {
    double emission_time;
    double reception_time;
    double radar_time;
    double radar_distance;
};
```

Implementeer:

\[
T_{\rm radar}=\frac{T_++T_-}{2},
\qquad
R_{\rm radar}=\frac{c(T_+-T_-)}{2},
\]

met causaliteitsguard \(T_+\geq T_-\).

**Lorentz-map**

```cpp
struct LorentzMapResult {
    std::array<double, 4> transformed_event;
    double gamma;
    double invariant_residual;
};
```

Voor willekeurige boostrichting wordt gerapporteerd:

\[
\Delta_s=
\frac{|s'^2-s^2|}{|s^2|+s_0^2}.
\]

Test inverse boost, collineaire compositie, nulboost, lage-snelheidslimiet en near-\(c\)-domeincontrole.

**QSS-eigenproblem**

```cpp
struct QSSSpectrumResult {
    std::vector<std::complex<double>> eigenvalues;
    double eigen_residual;
    double conditioning;
    std::string epistemic_status; // exportstring; CheckKind pas na 0.8.27 retrofit
};
```

Voor:

\[
Ax=\lambda Bx
\]

gebruik een genormaliseerde eigenresidual. Zonder concrete SST-operator is de uitkomst synthetische lineaire-algebra-diagnostiek.

**Pseudospectrum**

Bereken:

\[
\|(zI-A)^{-1}\|
\]

op een gedocumenteerd grid, inclusief conditioning en singulariteitsgedrag.

**Nieuwe tests**

- Minkowski-invariantie;
- radar roundtrip;
- diagonale en Jordan-matrices;
- non-normal matrix met bekend gedrag;
- near-singular foutpaden;
- Python/Node parity;
- statuslabels in evidence.

## Out of scope


- Claim “QSS closed physics”.
- Preferred-frame full scan.
- Afleiding van Lorentzsymmetrie uit SST-microdynamica.
- Productieinterpretatie van synthetische spectra als deeltjesvoorspellingen.

## Exit


- Beide versies `0.8.22`.
- Radar- en Lorentzhelpers zijn numeriek stabiel, dimensie-expliciet en getest.
- QSS-uitvoer draagt machineleesbaar `CONDITIONAL_BRIDGE`, `OPEN_RESEARCH_GATE` of `SYNTHETIC_DIAGNOSTIC` (strings; enum-retrofit in 0.8.27).
- Geen documentatie presenteert synthetische QSS-scaffolding als gesloten fysica.
- Python/Node parity en volledige CI groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.22: operational spacetime and QSS scaffolding`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
