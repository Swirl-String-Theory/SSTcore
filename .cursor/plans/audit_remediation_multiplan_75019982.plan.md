---
name: Audit remediation multiplan
overview: "Volledige audit-remediatie (A+B+C) op nieuwe epic-branch; vier deelplannen, elk met eigen commit (message = plantitel)."
todos:
  - id: branch-epic
    content: "Nieuwe branch sstcore/audit-remediation-0.8.28 vanaf HEAD van 0.8.28 (vóór R0)"
    status: pending
  - id: r0-ingest
    content: "Deelplan R0: audit archiveren + commit met plantitel"
    status: pending
  - id: r1-blockers
    content: "Deelplan R1: blockers B-001..B-005 + H-008 + commit met plantitel"
    status: pending
  - id: r2-scientific
    content: "Deelplan R2: H-001..H-007 + commit met plantitel"
    status: pending
  - id: r3-product-zip
    content: "Deelplan R3: M-001..M-006 + zip + commit met plantitel"
    status: pending
isProject: false
---

# SSTcore audit-remediatie (A+B+C in 4 deelplannen)

**Bron:** [`SSTcore_v0.8.28_high_resolution_audit.md`](c:\Users\oscar\Downloads\SSTcore_v0.8.28_high_resolution_audit.md), findings JSON, evidence zip.  
**Verdict:** niet release-ready; doel na alle deelplannen: blockers + high + medium dicht, daarna nieuwe lean source-zip.  
**Versie:** blijft **0.8.28** (remediatie van rc1; geen canon-bump).  
**Conventies:** [`SHARED_CONVENTIONS.md`](c:\workspace\projects\SSTcore\.cursor\plans\SHARED_CONVENTIONS.md) — CI-poort per deelplan; **één commit per deelplan** (verplicht in dit epic).

## Git: epic-branch + commits

**Branch (aanmaken bij start uitvoering, vóór R0):**

```text
sstcore/audit-remediation-0.8.28
```

- Basis: huidige `HEAD` van branch `0.8.28` (`git checkout -b sstcore/audit-remediation-0.8.28`).
- Alle R0–R3-commits landen op deze branch; **niet** pushen tenzij gevraagd.
- Geen unrelated dirty tree meenemen (IDE, zip, validation logs, examples WIP) tenzij dat deelplan ze bewust toevoegt.

**Commit na elk deelplan (verplicht bij exit):** subjectregel = **plantitel** van dat deelplan; body = 1 zin scope.

| Deelplan | Commit subject (plantitel) |
|---|---|
| R0 | `SSTcore audit R0: Audit ingest` |
| R1 | `SSTcore audit R1: Patch set A blockers + H-008` |
| R2 | `SSTcore audit R2: Patch set B scientific guards` |
| R3 | `SSTcore audit R3: Patch set C product + source zip` |

```mermaid
flowchart LR
  branch[branch epic] --> R0[R0 ingest commit]
  R0 --> R1[R1 blockers commit]
  R1 --> R2[R2 scientific commit]
  R2 --> R3[R3 product zip commit]
```

Bij goedkeuring van dit masterplan: schrijf vier aparte bestanden onder [`SSTcore/.cursor/plans/`](c:\workspace\projects\SSTcore\.cursor\plans\) (met dezelfde commit-subjects) en voer **strikt sequentieel** uit: branch → R0 → R1 → R2 → R3. Niet parallel.

---

## Deelplan R0 — Audit ingest

**Bestand:** `audit_r0_ingest.plan.md`  
**Doel:** auditartefacten vastleggen in de repo (geen productcode).

- Kopieer naar `SSTcore/.cursor/audits/v0.8.28/`:
  - `SSTcore_v0.8.28_high_resolution_audit.md`
  - `SSTcore_v0.8.28_audit_findings.json`
  - evidence zip (of uitgepakte logs + `CMakeLists.audit-build-only.patch`)
- Korte `README.md` met SHA-256 van de geauditte bundle en link naar R1–R3.
- Geen C++/Python/Node wijzigingen.

**Exit:** artefacten aanwezig; **commit** met subject `SSTcore audit R0: Audit ingest`.

---

## Deelplan R1 — Patch set A (blockers) + H-008

**Bestand:** `audit_r1_blockers.plan.md`  
**Findings:** B-001, B-002, B-003, B-004, B-005, H-008

| ID | Concrete fix |
|---|---|
| B-002 | Extraheer `bind_qss_spectroscopy` uit [`operational_spacetime_node.cpp`](c:\workspace\projects\SSTcore\src\operational_spacetime_node.cpp) naar nieuw [`src/qss_spectroscopy_node.cpp`](c:\workspace\projects\SSTcore\src\qss_spectroscopy_node.cpp); voeg toe aan `sstcore_node` in [`CMakeLists.txt`](c:\workspace\projects\SSTcore\CMakeLists.txt). |
| B-003 | Bij Linux `--no-undefined`: `target_link_libraries(sstcore PRIVATE Python::Python)` (of equivalent `Python::Module` policy) waar de pybind-extensie wordt gebouwd — zelfde intentie als audit-only patch. |
| B-004 | Vervang FNV-als-SHA-256 in [`pipeline_provenance.cpp`](c:\workspace\projects\SSTcore\src\pipeline_provenance.cpp), [`geometry_certificate.cpp`](c:\workspace\projects\SSTcore\src\geometry_certificate.cpp), [`polygonal_smooth_certificate.cpp`](c:\workspace\projects\SSTcore\src\polygonal_smooth_certificate.cpp) door echte SHA-256 over canonieke bytes (kleine portable `sha256` helper in `src/` of `include/`; geen OpenSSL-dependency tenzij al aanwezig). Valideer 64-hex velden bij certify. |
| B-005 | In [`sst_kam_diagnostics.cpp`](c:\workspace\projects\SSTcore\src\sst_kam_diagnostics.cpp): n>2 via LU/Gaussian det of rank; singuliere Hessiaan → `Indeterminate` (niet Pass). Adversarial 3×3 regressietest. |
| H-008 | In [`src/SSTcore/__init__.py`](c:\workspace\projects\SSTcore\src\SSTcore\__init__.py) `get_resources_dir`: vanaf `src/SSTcore` drie levels omhoog naar repo-root `resources/` (nu `parent.parent` = `src/resources`). |
| B-001 | Manifest-script `scripts/check_source_bundle_manifest.py` (+ lijst van verplichte paden: o.a. `scripts/`, `lib/`, `README.md`, `LICENSE`); nog **geen** volledige zip-rebuild hier — die zit in R3. Wel ontbrekende *repo*-paden herstellen als package.json/tests ze eisen. |

**Exit:** adversarial KAM + provenance hash-tests groen; pytest zonder `SSTCORE_RESOURCES` voor resource-discovery; Node QSS-bestand in CMake; CI-poort SHARED; **commit** `SSTcore audit R1: Patch set A blockers + H-008`.

---

## Deelplan R2 — Patch set B (scientific guards)

**Bestand:** `audit_r2_scientific.plan.md`  
**Findings:** H-001 … H-007

| ID | Concrete fix |
|---|---|
| H-001 | Action-phase: `delta_shape_separability`, coupled momentum–shape countermodel, fixed-V `γ²−1` guard in `sst_action_phase*` + regressies. |
| H-002 | Schaal-veilige formules (`V = c*((P*c)/H)`), genormaliseerde residuals, status finite/valid/tolerance scheiden. |
| H-003 | Provenance certify: strikte 64-hex hashes, timestamp-format, exacte stage-transitions, reject malformed. |
| H-004 | Polygonal-smooth: huidige Pass → `Diagnostic`/`Indeterminate` (of hernoemde status); Pass alleen met reach/isotopy (nog niet) — downgrade claim. |
| H-005 | Core torsion: echte `dimensional_residual`; anisotropy volle matrix + symmetrie-check. |
| H-006 | Evidence JSON: library of strikte encoder (escape control chars, reject NaN/Inf), volle precisie, schema/version velden. |
| H-007 | QSS: hernoem `conditioning` → bv. `eigenvalue_magnitude_ratio`; documenteer; voeg echte conditioning-metric toe of markeer OPEN_RESEARCH. |

**Exit:** nieuwe/uitgebreide tests voor elk H-finding; suite groen; **commit** `SSTcore audit R2: Patch set B scientific guards`.

---

## Deelplan R3 — Patch set C (product) + nieuwe zip

**Bestand:** `audit_r3_product_zip.plan.md`  
**Findings:** M-001 … M-006 + B-001 zip-regeneratie

| ID | Concrete fix |
|---|---|
| M-001 | Operational spacetime: directionele boosts + dimensieloze residual-normalisatie (geen `abs(s2)+1.0` als verborgen schaal). |
| M-002 | Contact/rank: gescheiden epsilons, domain-checks, conditioning-ceiling op rank-9 Pass. |
| M-003 | `npm test` draait alle nieuwe Node-tests; `index.d.ts` expliciete types voor 0.8.20–0.8.28 API’s. |
| M-004 | `list_bindings`: classes correct via `PyType_Check` (of pybind equivalent). |
| M-005 | Wheel/package: stale `py_modules` opruimen, resource package discovery, license metadata. |
| M-006 | Zip-mtime normaliseren bij bundle-build. |
| B-001 | Regenereer `SSTcore-source-bundle-0.8.28.zip` met uitgebreide include-lijst (vorige lean plan **plus** `scripts/`, `lib/`, `README.md`, `LICENSE`; `docs/` alleen als package/tests het eisen). Manifest-check moet slagen. Geen `.pyd/.zip/.stl/.bin`, geen `.rr/`; knots overlay + `knotplot_knots_data.js` behouden. |

**Exit:** manifest CI groen; nieuwe zip geverifieerd; npm test + pytest + native tests groen; **commit** `SSTcore audit R3: Patch set C product + source zip` (zip zelf alleen committen als expliciet gewenst; default: zip lokaal, script/manifest wél in commit).

---

## Uitvoeringsregels

- Eerst branch `sstcore/audit-remediation-0.8.28`, daarna R0→R1→R2→R3.
- Per deelplan: baseline pytest/npm → code → suite → nieuwe tests → suite → **commit met plantitel**.
- Audit evidence zelf niet wijzigen; code volgt `required_action` uit findings.
- Geen Zenodo mint/push; geen force-push.
- Masterplan-bestand niet herschrijven tijdens uitvoering van deelplannen; wel status in elk deelplan-bestand.
