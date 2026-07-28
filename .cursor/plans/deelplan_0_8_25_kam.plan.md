---
name: Deelplan 0.8.25 KAM
overview: "Bump beide naar 0.8.25. KAM-S vs KAM-T, stage-1 diagnostics, ladder enum KAM-0…5, golden-ratio null-test only."
todos:
  - id: d825-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d825-version-bump
    content: "Bump beide → 0.8.25"
    status: pending
  - id: d825-kam-module
    content: "sst_kam_diagnostics: Omega, Hessian, resonance, Diophantine + ladder structs"
    status: pending
  - id: d825-bind
    content: "Python/Node bind + capabilities"
    status: pending
  - id: d825-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d825-new-tests
    content: "CI stap 4–5: stage-1 + null-test + 100%"
    status: pending
  - id: d825-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.25: KAM stage-1 diagnostics"
    status: pending
isProject: false
---

# Deelplan 0.8.25 — KAM-caged knot-state

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_24_core_torsion.plan.md](deelplan_0_8_24_core_torsion.plan.md)  
**Next:** [deelplan_0_8_26_fmax_provenance.plan.md](deelplan_0_8_26_fmax_provenance.plan.md)  
**Target:** beide **"0.8.25"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — hergebruik `CertificateStatus`; `KAMStage` 2–5 = **scaffolding placeholders** (geen claim zonder extra certificaten).

## Must-ship

```text
include/sst_kam_diagnostics.h
src/sst_kam_diagnostics.cpp
src/sst_kam_diagnostics_py.cpp
src/sst_kam_diagnostics_node.cpp
# + CMake/setup src_files + bind_* in module_sst/module_node
tests/test_kam_diagnostics.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.25/`
- `SST-CANON/been_processed/sources/v0.8.25_kam_caged_knot/`, `.../v0.8.25_clean_patch/`

## CI-poort


1. Baseline Python/Node/parity groen.
2. KAM-stage-1-productiecode en wiring toevoegen, nog zonder nieuwe tests.
3. Regressie: bestaande suite 100% groen.
4. Stage-1-, resonantie-, conditioning-, null-test- en paritytests toevoegen.
5. Final: capabilities, docs, bindings en versievelden bijgewerkt.

## Scope


- Version bump → `0.8.25`.
- `include/sst_kam_diagnostics.h` + `src/sst_kam_diagnostics.{cpp,_py,_node}.cpp`.
- \(\Omega_i=\partial H_0/\partial I_i\), Hessian \(D_{ij}\), non-degeneracy en conditioning.
- Resonantie \(|k\cdot\Omega|\), Diophantische screening.
- KAM-S versus KAM-T; ladder enum `KAM-0…KAM-5`.
- Golden ratio uitsluitend als null-test, niet als centreline of afgeleide natuurconstante.

**Beoogde typen**

```cpp
enum class KAMSector { S, T };
enum class KAMStage { KAM0, KAM1, KAM2, KAM3, KAM4, KAM5 };

struct ResonanceCandidate {
    std::vector<int> k;
    double detuning;
    int order;
};

struct KAMStage1Result {
    KAMSector sector;
    KAMStage achieved_stage;
    std::vector<double> frequencies;
    std::vector<double> hessian;
    double hessian_determinant;
    double minimum_detuning;
    double diophantine_margin;
    CertificateStatus status;
};
```

**Derivatieven**

Ondersteun:

- analytische callbacks;
- finite differences met gerapporteerde stapgrootte;
- conditioning en foutschatting.

**Non-degeneracy**

Test:

\[
\det D\neq0
\]

of gebruik een numeriek robuuste SVD-classificatie. Rapporteer singular values en condition number.

**Resonantiescan**

Voor gehele \(\mathbf k\) tot \(K_{\max}\):

\[
\Delta_{\mathbf k}=|\mathbf k\cdot\boldsymbol\Omega|.
\]

Bewaar de kleinste kandidaten en hun orde.

**Diophantische screen**

Conditioneel:

\[
|\mathbf k\cdot\boldsymbol\Omega|
\geq
\frac{\gamma_K}{|\mathbf k|^\nu}.
\]

Een eindige scan levert geen universeel KAM-bewijs.

**Nieuwe tests**

- niet-resonante integrabele oscillator;
- exact resonant en bijna-resonant systeem;
- singuliere en slecht-geconditioneerde Hessian;
- golden-ratio null-test;
- gate die verhindert dat stage hoger dan KAM-1 wordt geclaimd zonder aanvullende certificaten;
- Python/Node parity.

## Out of scope


- Nonrelease T(6,9)/mod-9-composieten als release-default.
- Volledige Floquet/Krein-productiepipeline.
- Bewijs van langdurige KAM-stabiliteit uit alleen een eindige stage-1-scan.
- Golden ratio als voorkeursgeometrie.

## Exit


- Beide versies `0.8.25`.
- KAM-S en KAM-T zijn technisch en documentair onderscheiden.
- Stage-1-output bevat frequenties, Hessian, conditioning en resonantiekandidaten.
- Eindige scans worden nergens als volledig KAM-stabiliteitsbewijs gepresenteerd.
- Golden-ratio-test draagt expliciet null-teststatus.
- Python/Node parity en volledige CI groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.25: KAM stage-1 diagnostics`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
