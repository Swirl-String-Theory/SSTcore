---
name: Deelplan 0.8.21 Certification Biot
overview: "Bump beide naar 0.8.21. Ridgerunner polygonal→smooth certification hooks + bounded-domain Biot–Savart diagnostic gates."
todos:
  - id: d821-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d821-version-bump
    content: "Bump beide → 0.8.21"
    status: pending
  - id: d821-ridgerunner-gates
    content: "Polygonal→smooth certification gate structs/API"
    status: pending
  - id: d821-biot-diagnostics
    content: "Bounded-domain Biot–Savart diagnostic helpers op bestaande biot_savart"
    status: pending
  - id: d821-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d821-new-tests
    content: "CI stap 4–5: nieuwe tests + 100%"
    status: pending
  - id: d821-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.21: polygonal–smooth and Biot–Savart gates"
    status: pending
isProject: false
---

# Deelplan 0.8.21 — Certification / Biot gates

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_20_geometry_contact.plan.md](deelplan_0_8_20_geometry_contact.plan.md)  
**Next:** [deelplan_0_8_22_spacetime_qss.plan.md](deelplan_0_8_22_spacetime_qss.plan.md)  
**Target:** beide **"0.8.21"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — **hergebruik** `CertificateStatus` uit 0.8.20 (niet herdefiniëren).

## Must-ship

```text
src/polygonal_smooth_certificate.{h,cpp,_py,_node}.cpp   # of onder tube/
# Biot gate: helpers in/naast src/biot_savart.*
tests/test_polygonal_smooth_certificate.py
tests/test_biot_savart_gate.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.21/`
- `SST-CANON/been_processed/sources/v0.8.21_eight_source_patch_series/` (focus 0004 Biot, 0008 Ridgerunner)

## CI-poort


1. Baseline Python/Node/parity vastleggen.
2. Productiecode en wiring toevoegen zonder nieuwe tests.
3. Bestaande tests opnieuw 100% groen.
4. Certification-, foutpad-, convergentie- en paritytests toevoegen.
5. Final: volledige suite groen; capabilities en binding coverage bijgewerkt.

## Scope


- Version bump → `0.8.21`.
- Ridgerunner polygonal→smooth certification hooks; geen volledige Ridgerunner-port.
- Bounded-domain Biot–Savart operator diagnostics op [src/biot_savart.*](../../src/biot_savart.cpp).
- Capability flags in Node `GetCapabilities` indien nieuw.

**Representatiecontract**

Iedere certificatie-invoer specificeert:

- polygonale punten/segmenten;
- gladde interpolant of Fouriercoëfficiënten;
- parametrisatie en oriëntatie;
- schaalconventie en tube radius;
- bron- en outputhash.

**Polygonal→smooth certificate**

```cpp
struct PolygonalSmoothCertificate {
    CertificateStatus status;
    double hausdorff_bound;
    double tangent_error;
    double curvature_error;
    double thickness_lower_bound;
    std::string polygon_hash;
    std::string smooth_hash;
};
```

Bereken of schat:

\[
d_H(P,S),
\qquad
\max_s\|\hat t_P-\hat t_S\|,
\qquad
\Delta\kappa,
\]

plus een conservatieve thickness-ondergrens. Niet-bewijsbare bounds geven `Indeterminate`.

**Topologieguard**

Een “same knot”-claim vereist een expliciete voldoende voorwaarde, bijvoorbeeld een geldige isotopie-tube-margin. Visuele overeenkomst of alleen lage RMS-fout is onvoldoende.

**Biot–Savart gate**

```cpp
struct BiotSavartGateResult {
    CertificateStatus status;
    double observable;
    double estimated_limit;
    double relative_residual;
    double boundary_margin;
    std::size_t sample_count;
    std::string regularization_id;
};
```

Rapporteer domeingrootte, afstand tot grens, regularisatie, resolutie en residual. Voor de gebruikelijke target:

\[
\Delta_A=\left|4\pi A_K-1\right|.
\]

**Nieuwe tests**

- analytische cirkel;
- polygonale verfijningsreeks;
- bewust te grove smooth fit;
- te klein domein;
- ontbrekende regularisatie-ID;
- hash mismatch;
- C++/Python/Node parity.

## Out of scope


- Volledige \(N\to32000\)-convergentiesweep.
- Nieuwe Ridgerunner-optimalisatie.
- Volledige isotopie-bewijsengine.
- Alle acht research-trackappendices als productie-solvers.

## Exit


- Beide versies `0.8.21`.
- Iedere smooth-geometrie kan naar haar polygonale bron en hashes terugwijzen.
- Certificaten bevatten numerieke bounds, niet alleen booleans.
- Biot–Savart-uitvoer vermeldt resolutie, domein, grensmarge en regularisatie.
- Een coarse gate wordt nergens als hoge-resolutiecertificaat gepresenteerd.
- Alle nieuwe tests en parity groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.21: polygonal–smooth and Biot–Savart gates`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
