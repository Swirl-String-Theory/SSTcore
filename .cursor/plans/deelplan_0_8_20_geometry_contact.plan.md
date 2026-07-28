---
name: Deelplan 0.8.20 Geometry Contact
overview: "Bump beide naar 0.8.20. Geometry-certificate afronden/exponeren; contact-pressure saturation + Chronos first-hitting + rank-9 diagnostics op bestaande kernels."
todos:
  - id: d820-ci-baseline
    content: "CI stap 1: pytest + npm test + test:parity groen (na Deelplan 0)"
    status: pending
  - id: d820-version-bump
    content: "Bump beide versies → 0.8.20 (header, setup.py, package.json, __init__, test pins)"
    status: pending
  - id: d820-geometry-api
    content: "Geometry-certificate gates/labels exposen (resolved-tube / protocol v0.1)"
    status: pending
  - id: d820-contact-chronos
    content: "Contact saturation + Chronos hitting + rank-9 diagnostic structs + py/node bind"
    status: pending
  - id: d820-ci-regress
    content: "CI stap 3: regressie 100% groen"
    status: pending
  - id: d820-new-tests
    content: "CI stap 4–5: nieuwe tests + alles 100% groen"
    status: pending
  - id: d820-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.20: geometry certificate and contact/Chronos gates"
    status: pending
isProject: false
---

# Deelplan 0.8.20 — Geometry + contact / Chronos

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_baseline.plan.md](deelplan_0_baseline.plan.md)  
**Next:** [deelplan_0_8_21_certification_biot.plan.md](deelplan_0_8_21_certification_biot.plan.md)  
**Target:** beide **"0.8.20"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — introduceert **`CertificateStatus`** (gate-uitslag; niet pipeline-certified).

## Must-ship

```text
include/sst/certificate_status.h          # of equivalent gedeelde header
src/geometry_certificate.{h,cpp,_py,_node}.cpp   # of uitbreiding tube/geometry_*
# contact/Chronos/rank9: uitbreiding contact_stress + chronos_kelvin_* of dunne wrappers
tests/test_geometry_certificate.py
tests/test_contact_saturation.py
tests/test_chronos_first_hitting.py
tests/test_rank9_diagnostics.py
(+ Node parity asserts waar van toepassing)
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.20/`
- `SST-CANON/been_processed/sources/v0.8.20_contact_pressure_saturation.patch` (+ chronos/rank9; SSDL = research, geen pin)

## CI-poort


1. Baseline: Python + Node + parity groen en logs bewaren.
2. Productiecode: geometry/contact/Chronos/rank-9 implementeren, nog zonder nieuwe testbestanden.
3. Regressie: bestaande suite 100% groen.
4. Nieuwe tests: unit-, foutpad-, binding- en paritytests toevoegen.
5. Final: alles groen; `BINDING_COVERAGE.md`, capabilities en versievelden bijgewerkt.

## Scope


- Version bump overal naar `0.8.20`.
- Geometry-certificate: bestaande resolved-tube / [GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md](../../docs/GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md) — publieke gate-helpers/capabilities waar nog ontbrekend.
- Contact-pressure saturation + Swirl-Clock shielding op `src/tube/contact_stress.*`.
- Chronos–Kelvin first-hitting / kink-vs-reconnection ledger als dunne API.
- Rank-nine contact-channel diagnostic struct + guard status.
- Wire: `module_sst.cpp` / `module_node.cpp` / CMake / setup indien nieuwe TU’s.

**Gemeenschappelijke statusenum**

```cpp
enum class CertificateStatus {
    Pass,
    Fail,
    Indeterminate,
    NotEvaluated
};
```

Ontbrekende input mag nooit impliciet `Pass` opleveren.

**Geometry-certificate API**

```cpp
struct GeometryCertificate {
    CertificateStatus status;
    double minimum_separation;
    double minimum_radius_of_curvature;
    double tube_radius;
    double thickness_margin;
    double discretization_error;
    std::string geometry_hash;
};
```

De gate controleert minimaal:

\[
d_{\min}>2a,
\qquad
a\kappa_{\max}\leq 1,
\]

met expliciete tolerantie en discretisatiefout.

**Contact-pressure saturation**

```cpp
struct ContactSaturationResult {
    CertificateStatus status;
    double peak_contact_pressure;
    double saturation_pressure;
    double saturation_ratio;
    std::size_t active_contact_count;
};
```

Gebruik:

\[
S_p=\frac{p_{\max}}{p_{\mathrm{sat}}}.
\]

Classificeer onder, op en boven de drempel met een expliciete \(\varepsilon\). Dit blijft een diagnostische gate, geen full-CFD-oplossing.

**Chronos first-hitting**

```cpp
struct ChronosFirstHittingResult {
    CertificateStatus status;
    double first_hitting_time;
    std::size_t event_index;
    double threshold;
};
```

Definieer:

\[
t_*=\inf\{t\geq0:g(t)\geq g_*\},
\]

inclusief interpolatie, no-hit gedrag en de gebruikte observable.

**Rank-nine diagnostics**

```cpp
struct Rank9ChannelDiagnostics {
    CertificateStatus status;
    int numerical_rank;
    std::array<double, 9> singular_values;
    double conditioning;
};
```

Bereken rang via:

\[
\sigma_i/\sigma_{\max}>\tau_{\rm rank}.
\]

`rank == 9` is een numerieke diagnose, niet automatisch een fysische closure.

**Nieuwe tests**

- analytische cirkel met bekende kromming;
- geldige resolved tube;
- bekende self-contact failure;
- no-hit en exact-hit Chronos-cases;
- rank-8, rank-9 en slecht-geconditioneerde matrices;
- ontbrekende invoer → `Indeterminate`;
- Python/Node parity en JSON-serialisatie.

## Out of scope


- SSDL als `RHO_FLUID_CANON`-vervanging.
- Volledige contact-CFD, dynamische reconnection of full rank-9 solver.
- Bewijs dat numerieke rang negen een fysische selectieprincipie oplevert.
- Nieuwe ideale-knoopoptimalisatie.

## Exit


- Beide versies `0.8.20`.
- Alle certificate-uitkomsten bevatten status, tolerantie, foutmaat en geometriehash.
- Geen publieke gate retourneert `CertificateStatus::Pass` zonder voldoende invoer (geen impliciete Pass).
- `PipelineCertificationStatus::Certified` bestaat pas in 0.8.23 — hier niet gebruiken.
- Contact-, Chronos- en rank-9-API’s zijn in Python en Node gelijkwaardig.
- Bestaande resolved-tube-tests blijven groen; nieuwe tests en parity zijn 100% groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.20: geometry certificate and contact/Chronos gates`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
