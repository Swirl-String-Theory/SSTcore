---
name: Deelplan 0.8.24 Core Torsion
overview: "Bump beide naar 0.8.24. Core–torsion M=E0 I/c_T^2 (geen factor 2), residuals chi-hat/delta_aniso, link-gate/star-basis scaffolding + failure classes."
todos:
  - id: d824-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d824-version-bump
    content: "Bump beide → 0.8.24"
    status: pending
  - id: d824-torsion-api
    content: "core_torsion module: M_torsion, chi_hat, delta_aniso + py/node"
    status: pending
  - id: d824-link-gate
    content: "Link-field phase-gate / star-basis / failure-class E/T/N/M scaffolding"
    status: pending
  - id: d824-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d824-new-tests
    content: "CI stap 4–5: factor-2 regressietest + 100%"
    status: pending
  - id: d824-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.24: core–torsion mass without factor two"
    status: pending
isProject: false
---

# Deelplan 0.8.24 — Core–torsion + link-gate

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_23_provenance.plan.md](deelplan_0_8_23_provenance.plan.md)  
**Next:** [deelplan_0_8_25_kam.plan.md](deelplan_0_8_25_kam.plan.md)  
**Target:** beide **"0.8.24"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — `OpenResearchGate` tot 0.8.27 als **string** `OPEN_RESEARCH_GATE`.

## Must-ship

```text
include/sst_core_torsion.h
src/core_torsion.{cpp,_py,_node}.cpp
include/sst_link_field_gate.h          # scaffolding OK als dun
src/link_field_gate.{cpp,_py,_node}.cpp
tests/test_core_torsion.py             # factor-2 faalt, E0/c_T^2 slaagt
tests/test_link_field_gate.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.24/`
- `SST-CANON/been_processed/sources/v0.8.24_core_torsion_phase_gate/` (+ `SOURCE_CLAUDE_CLEANUP_PACKAGE.md` P1)

## CI-poort


1. Baseline Python/Node/parity groen.
2. Formulecorrectie, residuals en gate-scaffolding implementeren zonder nieuwe tests.
3. Regressie: bestaande suite volledig groen.
4. Factor-2-, dimensie-, residual-, failure-class- en paritytests toevoegen.
5. Final: deprecations, docs, bindings en versievelden compleet.

## Scope


- Version bump → `0.8.24`.
- \(M_{\rm torsion}=E_0 I / c_T^2\), niet \(2E_0 I / c_T^2\).
- Residuals: \(\hat\chi = c_T^2 \mathrm{tr}(M)/(3 E_0)\) en \(\delta_{\rm aniso}\).
- Link-field phase-gate / star-basis \((\rho_\star,\Gamma_\star,r_\star)\) scaffolding.
- Failure-class enum: `E / T / N / M`.
- Module bijvoorbeeld `src/core_torsion.*` plus optioneel `src/link_field_gate.*`.

**Core–torsion API**

```cpp
struct TorsionMassResult {
    double mass;
    double dimensional_residual;
    std::string convention;
};
```

Valideer:

\[
E_0\geq0,
\qquad
I\geq0,
\qquad
c_T>0.
\]

De dimensie van \(I\) moet expliciet in het API-contract staan.

**Migratie van de factor-2-route (keuze vastgelegd)**

Gebruik **nieuwe functienaam** + deprecatie van de oude:

- Nieuw: `torsion_inertial_mass(E0, I, c_T)` → \(E_0 I / c_T^2\)
- Legacy (opt-in): `torsion_inertial_mass_legacy_factor2(...)` gemarkeerd deprecated; alleen voor regressieguards
- Geen stille semantische wijziging van een bestaande publieke naam zonder deprecationperiode

**Anisotropieresiduals**

```cpp
struct AnisotropyResiduals {
    double chi_hat;
    double delta_aniso;
    double normalization;
};
```

Documenteer:

- absolute en relatieve varianten;
- nuldenominatorgedrag;
- normalisatie;
- tolerantie;
- status bij onvoldoende tensorinformatie.

**Link-gate scaffolding**

```cpp
enum class LinkGateFailure {
    None,
    E,
    T,
    N,
    M
};
```

De gate bevat inputvalidatie, star-basisadministratie, fase-/normalisatieresidual en failure class. Ontbrekende theoretische closure: string `OPEN_RESEARCH_GATE` (CheckKind-retrofit in 0.8.27).

**Nieuwe tests**

- historische factor-2-target faalt;
- gecorrigeerde target slaagt;
- dimensie- en nulinputtests;
- isotrope null case;
- gecontroleerde anisotropie;
- iedere failure class;
- Python/Node parity;
- provenance-records voor gate-input.

## Out of scope


- Volledige 3+1 lattice-QCD-achtige simulatie.
- Action–phase mass-shell.
- Bewijs van link-field closure.
- Stilzwijgende verwijdering van legacy-API’s zonder deprecationperiode.

## Exit


- Beide versies `0.8.24`.
- Geen productiepad gebruikt onbedoeld de factor twee.
- Tests tonen expliciet dat de factor-2-target faalt en \(E_0 I/c_T^2\) slaagt.
- Alle residuals hebben gedocumenteerde normalisatie en foutstatus.
- Link-gates geven specifieke `E/T/N/M`-failure classes en claimen geen gesloten fysica.
- CI en parity 100% groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.24: core–torsion mass without factor two`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
