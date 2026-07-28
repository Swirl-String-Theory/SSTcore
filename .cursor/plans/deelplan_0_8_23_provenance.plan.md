---
name: Deelplan 0.8.23 Pipeline Provenance
overview: "Bump beide naar 0.8.23. KnotPlot→Ridgerunner→SSTcore/VortexLab pipeline-provenance API (PipelineCertificationStatus). Niet te verwarren met value-origin in 0.8.26."
todos:
  - id: d823-ci-baseline
    content: "CI stap 1: pytest + npm test + test:parity groen"
    status: pending
  - id: d823-version-bump
    content: "Bump beide → 0.8.23"
    status: pending
  - id: d823-provenance-api
    content: "Pipeline provenance record + PipelineCertificationStatus + bind py/node"
    status: pending
  - id: d823-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d823-new-tests
    content: "CI stap 4–5: tests/test_pipeline_provenance.py + parity + 100%"
    status: pending
  - id: d823-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.23: pipeline provenance records"
    status: pending
isProject: false
---

# Deelplan 0.8.23 — Pipeline provenance ladder

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_22_spacetime_qss.plan.md](deelplan_0_8_22_spacetime_qss.plan.md)  
**Next:** [deelplan_0_8_24_core_torsion.plan.md](deelplan_0_8_24_core_torsion.plan.md)  
**Target:** beide **"0.8.23"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — introduceert **`PipelineCertificationStatus`** (niet `CertificateStatus`).

## Must-ship

```text
include/sst_pipeline_provenance.h
src/pipeline_provenance.{cpp,_py,_node}.cpp
resources/schemas/pipeline_provenance.schema.json
examples/pipeline_provenance_manifest.example.json
tests/test_pipeline_provenance.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.23/`
- `SST-CANON/been_processed/sources/v0.8.23_genesis_link_field/SST_CANON-v0.8.23-CHANGELOG.md`

## CI-poort

1. Baseline Python/Node/parity vastleggen.
2. Provenance-schema, hashing en guards zonder nieuwe tests.
3. Regressie 100% groen.
4. Hash-, roundtrip-, tamper- en paritytests.
5. Final: schema, voorbeelden, capabilities, BINDING_COVERAGE.

## Scope

- Version bump → `0.8.23`.
- Pipeline metadata: KnotPlot → Ridgerunner → smoothing/Fourier → SSTcore/VortexLab.
- **`PipelineCertificationStatus`**: `Unknown`, `Candidate`, `Certified` ≠ `CertificateStatus::Pass`.
- Weiger `Certified` zonder minimale records + hashketen.

**Datamodel**

```cpp
enum class PipelineStage {
    KnotPlot, Ridgerunner, Smoothing, SSTcore, VortexLab
};

enum class PipelineCertificationStatus {
    Unknown, Candidate, Certified
};

struct ProvenanceRecord {
    PipelineStage stage;
    PipelineCertificationStatus certification;
    std::string tool_name;
    std::string tool_version;
    std::string input_sha256;
    std::string output_sha256;
    std::string parameter_sha256;
    std::string parent_record_sha256;
    std::string coordinate_convention;
    std::string scale_convention;
    std::string timestamp_utc;
};
```

**JSON-schema / hashing / guards:** zoals eerder — verplichte velden, deterministische SHA-256-normalisatie, `Certified` alleen bij complete geldige keten.

**Nieuwe tests:** geldige keten; gewijzigde coördinaat; ontbrekende stage; verkeerde schaal; hergebruikt certificaat; deterministische export; JSON-roundtrip; parity.

## Out of scope

- U(1) lattice simulator; notebook ingest; cloud backend.
- Value-origin / snapshot-vs-recompute (**0.8.26**).

## Exit

- Beide `0.8.23`; verifieerbare keten; byte-wijziging breekt hash; `Certified` zonder records onmogelijk; schema + parity groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.23: pipeline provenance records`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
