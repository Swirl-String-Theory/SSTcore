---
name: Deelplan 0.8.27 Epistemica
overview: "Bump beide naar 0.8.27. CheckKind enum, write_evidence_report, docs/label hygiene; geen fysica-break."
todos:
  - id: d827-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d827-version-bump
    content: "Bump beide → 0.8.27"
    status: pending
  - id: d827-checkkind
    content: "CheckKind enum + evidence report writer (py + optional native)"
    status: pending
  - id: d827-docs
    content: "RELEASE_NOTES / VERSION_MANAGEMENT / BINDING_COVERAGE hygiene"
    status: pending
  - id: d827-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d827-new-tests
    content: "CI stap 4–5: evidence-export tests + 100%"
    status: pending
  - id: d827-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.27: CheckKind and evidence export"
    status: pending
isProject: false
---

# Deelplan 0.8.27 — Hygiene / epistemica

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_26_fmax_provenance.plan.md](deelplan_0_8_26_fmax_provenance.plan.md)  
**Next:** [deelplan_0_8_28_action_phase.plan.md](deelplan_0_8_28_action_phase.plan.md)  
**Target:** beide **"0.8.27"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — **definitieve `CheckKind`**; retrofit eerdere string-velden.

## Must-ship

```text
include/sst_check_kind.h
include/sst_evidence_report.h
src/evidence_report.{cpp,_py,_node}.cpp   # writer mag py-first + thin native
tests/test_evidence_report.py
tests/test_check_kind.py
docs/epistemic_vocabulary.md              # of sectie in VERSION_MANAGEMENT
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.27/`

## CI-poort


1. Baseline Python/Node/parity groen en evidence bewaren.
2. `CheckKind`, evidence writer en docs implementeren zonder nieuwe tests.
3. Regressie: bestaande suite 100% groen; geen numerieke outputwijzigingen.
4. Schema-, roundtrip-, guard-, determinisme- en paritytests toevoegen.
5. Final: alle checks geclassificeerd, exports reproduceerbaar, volledige CI groen.

## Scope


- Version bump → `0.8.27`.
- `CheckKind` enum en machineleesbare epistemische classificatie.
- `write_evidence_report(path, checks, …)` met gelijke `sstcore_version` en `canon_version`.
- Buildmetadata: `git_commit`, `numeric_profile`, `compiler`, `platform`.
- Docs- en labelhygiene zonder numerieke formulewijzigingen.

**Retrofit (verplicht in dit deelplan)**

Map bestaande `epistemic_status` strings uit 0.8.22/24/26 naar `CheckKind` waar die modules al bestaan. Export blijft de gesloten vocabulaire-strings uit SHARED_CONVENTIONS.

**Uitgebreide `CheckKind`**

```cpp
enum class CheckKind {
    AlgebraicIdentity,
    CalibratedClosure,
    IndependentPrediction,
    NumericalConvergence,
    ConditionalBridge,
    OpenResearchGate,
    SyntheticDiagnostic
};
```

`SyntheticDiagnostic` is toegevoegd voor QSS- en andere synthetische testinputs.

**Resultaatmodel**

```cpp
struct CheckResult {
    std::string name;
    bool passed;
    CheckKind kind;
    double residual;
    double tolerance;
    bool supports_empirical_claim;
    std::string message;
};
```

`supports_empirical_claim` is standaard `false`; alleen expliciet aangewezen onafhankelijke datatests mogen dit op `true` zetten.

**Evidence metadata**

```cpp
struct EvidenceMetadata {
    std::string sstcore_version;
    std::string canon_version;
    std::string git_commit;
    std::string numeric_profile;
    std::string compiler;
    std::string platform;
};
```

**Evidence writer**

```python
SSTcore.write_evidence_report(
    path,
    checks,
    metadata,
    inputs
)
```

JSON bevat:

- gelijke package- en canonversie;
- commit en buildomgeving;
- inputhashes;
- checknaam, klasse, residual en tolerantie;
- `supports_empirical_claim`;
- timestamps;
- schema-versie.

**Labelhygiene**

Alleen SHARED_CONVENTIONS-exportstrings als machinevocabulaire. Menselijke labels (`OrthodoxForm`, `NotAnIndependentSSTDerivation`, `SyntheticInput`) alleen in docs/toelichting — mappen op `CONDITIONAL_BRIDGE` / `OPEN_RESEARCH_GATE` / `SYNTHETIC_DIAGNOSTIC`.

**Benchmarkguard**

Exact-closure-tabellen en resultaten moeten dragen:

```text
kind = CalibratedClosure
supports_empirical_claim = false
```

Een score als `111/111` moet per `CheckKind` kunnen worden uitgesplitst.

**Nieuwe tests**

- JSON-roundtrip;
- schema-validatie;
- onbekende enumwaarde;
- deterministische export;
- gewijzigde input verandert hash;
- calibrated closure kan niet ongemerkt als independent prediction worden geëxporteerd;
- Python/Node parity.

## Out of scope


- Nieuwe fysica-modules.
- Action–phase mass-shell.
- Numerieke formule- of constantenwijzigingen.
- Automatische empirische claim op basis van alleen een hoge pass rate.

## Exit


- Beide versies `0.8.27`.
- Iedere graded check heeft een `CheckKind`, residual, tolerantie en empirical-claimflag.
- Evidence-export bevat alle versie-, commit-, build- en inputhashvelden.
- `111/111` kan programmatically per checkklasse worden uitgesplitst.
- Geen bestaande numerieke output verandert.
- Schema-, roundtrip- en Python/Node paritytests zijn groen; CI 100%.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.27: CheckKind and evidence export`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
