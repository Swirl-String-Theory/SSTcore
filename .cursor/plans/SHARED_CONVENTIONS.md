# Gedeelde conventies (alle deelplannen)

Bron: [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)

## Optie A

`SSTCORE_VERSION == SSTCORE_CANON_VERSION` altijd (C++, Python, Node, pins).  
Python mag `SSTcore.CANON_VERSION` exporteren als **alias** van `__version__` (zelfde string), geen aparte compat-versie.

## CI-poort (verplicht)

1. Baseline: `python -m pytest tests/ -q` + `npm test` + `npm run test:parity`
2. Code **zonder** nieuwe testbestanden (versie-pins wél)
3. Zelfde suite opnieuw → 100%
4. Nieuwe tests toevoegen
5. Alles opnieuw → 100%
6. **Git commit** (verplicht) — zie hieronder

Artifacts (lokaal, niet committen tenzij expliciet gevraagd): `validation/baseline/`, `validation/baseline_inventory.json`.

## Git: één commit per deelplan (verplicht)

Na stap 5 (alles 100% groen) **altijd** een aparte commit voor dat deelplan. Geen bundeling van meerdere deelplannen in één commit.

**Regels:**

- Commit **alleen** wanneer de gebruiker dat in die chat goedkeurt / vraagt, of wanneer het deelplan expliciet “commit na exit” bevat en de gebruiker het deelplan heeft laten uitvoeren inclusief commit-stap.
- Commitmessage-stijl (voorbeeld):

```text
SSTcore v0.8.XX: <korte why — canon deelplan>

<1 zin scope: modules/API’s die dit deelplan toevoegt.>
```

- Inclusief: versiebumps, bronnen, tests, docs/`BINDING_COVERAGE` van **dit** deelplan.
- Exclusief: `validation/baseline/` logs, `__pycache__`, build artifacts, secrets.
- **Niet** pushen tenzij de gebruiker dat vraagt.
- Volgende deelplan start pas ná die commit (schone of bewuste working tree).

**Aanbevolen commit-titels:**

| Deelplan | Commit subject |
| --- | --- |
| 0 | `SSTcore v0.8.19: sync package and canon version` |
| 0.8.20 | `SSTcore v0.8.20: geometry certificate and contact/Chronos gates` |
| 0.8.21 | `SSTcore v0.8.21: polygonal–smooth and Biot–Savart gates` |
| 0.8.22 | `SSTcore v0.8.22: operational spacetime and QSS scaffolding` |
| 0.8.23 | `SSTcore v0.8.23: pipeline provenance records` |
| 0.8.24 | `SSTcore v0.8.24: core–torsion mass without factor two` |
| 0.8.25 | `SSTcore v0.8.25: KAM stage-1 diagnostics` |
| 0.8.26 | `SSTcore v0.8.26: Fmax provenance and M0(T) helpers` |
| 0.8.27 | `SSTcore v0.8.27: CheckKind and evidence export` |
| 0.8.28 | `SSTcore v0.8.28: action–phase mass-shell clock` |
| 0.8.29 | `SSTcore v0.8.29: rho_f provenance and dependency guards` |
| 0.8.30 | `SSTcore v0.8.30: density ontology and dimensional validator` |
| 0.8.31 | `SSTcore v0.8.31: rotor participation and phi_dyn diagnostics` |
| 0.8.32 | `SSTcore v0.8.32: rho_ref legacy and scaling audit` |
| 0.8.33 | `SSTcore v0.8.33: worldsheet form-degree guards` |
| 0.8.34 | `SSTcore v0.8.34: ideal-knot regime and Moffatt–Ricca` |
| 0.8.35 | `SSTcore v0.8.35: transverse projector 8pi/3 response` |
| 0.8.36 | `SSTcore v0.8.36: Maxwell spectro / kinetic / falsifier / swirl-tonic` |

## Canon-bronpaden

Altijd relatief t.o.v. SwirlStringTheory-repo:

```text
SST-CANON/been_processed/v0.8.XX/
SST-CANON/been_processed/sources/...
```

## Enums — eigendom & namen

| Enum | Introduced | Rol |
| --- | --- | --- |
| `CertificateStatus` {Pass, Fail, Indeterminate, NotEvaluated} | **0.8.20** | Numerieke/geometrische gate-uitslag |
| `PipelineCertificationStatus` {Unknown, Candidate, Certified} | **0.8.23** | Provenance-keten / certificatiestatus van records |
| `ValueOrigin` {CanonicalSnapshot, Recomputed, CalibratedInput} | **0.8.26** | Herkomst van een constante/waarde |
| `CheckKind` | **0.8.27** | Epistemische klasse van een check |
| `KAMSector` / `KAMStage` | **0.8.25** | KAM (stages 2–5 = scaffolding tot later) |
| `LinkGateFailure` {None,E,T,N,M} | **0.8.24** | Link-gate failure taxonomy |

**Verboden:** `CertificateStatus` hernoemen tot pipeline-status, of `certified` mengen met `Pass`.

## CheckKind (definitief in 0.8.27)

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

**Exportstrings (gesloten vocabulaire):**

```text
ALGEBRAIC_IDENTITY
CALIBRATED_CLOSURE
INDEPENDENT_PREDICTION
NUMERICAL_CONVERGENCE
CONDITIONAL_BRIDGE
OPEN_RESEARCH_GATE
SYNTHETIC_DIAGNOSTIC
```

Menselijke labels (alleen toelichting, geen machine-enum):

| Export | Menselijke toelichting (docs) |
| --- | --- |
| `CONDITIONAL_BRIDGE` | ConditionalBridge / OrthodoxForm (action–phase) |
| `OPEN_RESEARCH_GATE` | Open research / not an independent SST derivation |
| `SYNTHETIC_DIAGNOSTIC` | SyntheticInput / synthetic matrix diagnostic |

**Vóór 0.8.27:** modules gebruiken `std::string epistemic_status` met bovenstaande exportstrings (of tijdelijke literal). **Geen** `#include` van `CheckKind` tot 0.8.27. Daarna: retrofit string → enum in 0.8.22/24/28 modules.

## Ownership van gedeelde features

| Feature | Ships in | Later |
| --- | --- | --- |
| Geometry `CertificateStatus` | 0.8.20 | hergebruik 21/25 |
| Pipeline provenance | 0.8.23 | — |
| \(M_{\rm torsion}\) factor-2 fix | 0.8.24 | — |
| KAM stage-1 | 0.8.25 | ladder 2–5 later |
| \(M_0(T)\) bare-mass helpers | **0.8.26** | **0.8.28 alleen hergebruik** |
| Snapshot vs recompute | 0.8.26 | — |
| `CheckKind` + evidence-export | 0.8.27 | retrofit eerdere modules |
| Action–phase mass-shell | **0.8.28** | — |
| ρ_f dependency / provenance guards | **0.8.29** | hergebruik value_origin |
| Density ontology (`ρ_sub`/`ρ_eff`/`J_ω`/`μ_ℓ`) | **0.8.30** | — |
| Rotor / `φ_dyn` / `ℓ_ρ,eq` | **0.8.31** | — |
| `ρ_ref` legacy + A/B/C/Q/X scaling | **0.8.32** | breaking vs 0.8.28 defaults |
| Worldsheet two-form guards | **0.8.33** | — |
| Ideal-knot regime + Moffatt–Ricca | **0.8.34** | hergebruik writhe/twist/KKT |
| Transverse projector `8π/3` | **0.8.35** | — |
| Maxwell spectro / kinetic / falsifier / swirl-tonic | **0.8.36** | — |

## Wiring checklist (elk nieuw C++-module)

- `src/<mod>.{h,cpp}` (+ `include/` indien publiek header)
- `src/<mod>_py.cpp` + `bind_*` in `module_sst.cpp`
- `src/<mod>_node.cpp` + `bind_*` / capability in `module_node.cpp`
- `CMakeLists.txt` (`sstcore_lib` + targets)
- `setup.py` `src_files`
- `docs/BINDING_COVERAGE.md` + `gen_binding_manifest.py` indien van toepassing
