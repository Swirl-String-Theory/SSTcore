# Release Notes — SSTcore v0.8.36

Feature release: **SST Canon 0.8.19–0.8.36** as C++ / Python / Node APIs, Optie A version pins (`SSTCORE_VERSION` ≡ `SSTCORE_CANON_VERSION`), plus packaging, VortexLab, knot-resource, and audit work landed after **v0.8.18**.

Compared to **v0.8.18**, this is the recommended bundle for geometry certificates, provenance, mass-shell clocks, density/Maxwell diagnostics, and relaxed KnotPlot imports. Intermediate notes: [`RELEASE_NOTES_0.8.19.md`](RELEASE_NOTES_0.8.19.md), [`RELEASE_NOTES_0.8.28.md`](RELEASE_NOTES_0.8.28.md).

**npm package name:** `sst-core` (PyPI remains `SSTcore`).

---

## Version ladder (v0.8.18 → v0.8.36)

| Version | Module / change | Role |
|---------|-----------------|------|
| 0.8.19 | Optie A sync + smooth-tube metrics | Package ≡ canon; equilateral max-dev gate; spline arclength; `GEOMETRY_CERTIFICATE_PROTOCOL_v0.1` |
| 0.8.20 | `GeometryCertificateAPI` | Tube geometry, contact saturation, Chronos first-hitting, rank-9; `CertificateStatus` |
| 0.8.21 | `PolygonalSmoothCertificateAPI` + `BiotSavartGateAPI` | Polygonal→smooth bounds; bounded-domain Biot residual |
| 0.8.22 | `OperationalSpacetimeAPI` + `QSSSpectroscopyAPI` | Radar/Lorentz; synthetic QSS eigen/pseudospectrum |
| 0.8.23 | `PipelineProvenanceAPI` | KnotPlot→Ridgerunner→SSTcore/VortexLab chain; `PipelineCertificationStatus` |
| 0.8.24 | `CoreTorsionAPI` + `LinkFieldGateAPI` | \(M = E_0 I / c_T^2\) (no factor 2); link-gate E/T/N/M |
| 0.8.25 | `KAMDiagnosticsAPI` | KAM-S/T stage-1; golden-ratio null-test only |
| 0.8.26 | `ValueOriginAPI` + \(M_0(T)\) | Fmax snapshot vs recompute; Rydberg \(16\pi^2\); bare mass |
| 0.8.27 | `CheckKind` + `EvidenceReportAPI` | Epistemic export vocabulary |
| 0.8.28 | `ActionPhaseAPI` | Mass-shell clock \(H\), \(V\), \(\gamma\), \(d\tau/dT\), \(\Omega\) |
| 0.8.29 | `ValueOriginAPI` guards | \(\rho_f\) 2-sf provenance, dependency guard, VAM no-go |
| 0.8.30 | `DensityOntologyAPI` | \(\rho_\mathrm{sub}\) / \(\rho_\mathrm{eff}\) / \(J_\omega\) / \(\mu_\ell\) |
| 0.8.31 | `RotorParticipationAPI` | \(J_\omega^\mathrm{rot}\), \(\varphi_\mathrm{dyn}\), \(\ell_{\rho,\mathrm{eq}}\); twist vs Kelvin bend |
| 0.8.32 | `ScalingAuditAPI` | \(\rho_\mathrm{ref}\) legacy; \(P_\mathrm{cal}\) / \(P_\mathrm{open}\) / \(P_\mathrm{ref}\); A/B/C/Q/X |
| 0.8.33 | `WorldsheetGuardsAPI` | Form-degree / non-identification guards |
| 0.8.34 | `IdealKnotRegimeAPI` | \(\varepsilon_\kappa\), \(\varepsilon_\mathrm{sep}\); Moffatt–Ricca; LIA/KAM exclusion |
| 0.8.35 | `TransverseProjectorAPI` | \(8\pi/3\), \(R_0\), \(R_\mathrm{SST}\); HighRes vs Gilbert |
| 0.8.36 | spectro / kinetic / falsifier / swirl-tonic | Maxwell-stack diagnostics |

Coverage matrix: [`BINDING_COVERAGE.md`](BINDING_COVERAGE.md). Paired examples: `examples/example_*.py` + `examples/example_*.ts`.

---

## Changelog (v0.8.18 → v0.8.36)

### Packaging, Node, and VortexLab (with 0.8.19)

- npm package renamed to **`sst-core`** (registry name conflict); Python package stays `SSTcore`
- Node bindings colocated beside C++/Python twins; examples live as `example_*.py` / `example_*.ts`
- CI: Node 18/20/22/24; Linux GCC / macOS addon link fixes; OIDC npm publish; Actions Node 24 runtimes
- **VortexLab kernels in-tree** — curve sampling, filament velocity/integrator, intrinsic frame, rigid motion, knot catalog (`src/curve|filament|analysis|catalog`)
- Knot-dynamics C++ split into smaller TUs

### 0.8.19 — Optie A + geometry-certificate software layer

- `SSTCORE_CANON_VERSION` matches package version (Optie A); `tests/test_version_consistency.py`
- Equilateral gate uses **max relative edge deviation**, not `edge_length_rel_std` (retained as diagnostic)
- `PeriodicCubicSpline3D::integrated_arclength()` (Gauss–Kronrod); `length()` remains chord-parameter domain
- Combined smooth metrics: `SmoothTubeAnalyzer::analyze` / `analyze_smooth_resolved_tube`; always exports `ropelength_rad` and `ropelength_diam` (\(R_\mathrm{op,rad} = 2 R_\mathrm{op,diam}\))
- Protocol: [`GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md`](GEOMETRY_CERTIFICATE_PROTOCOL_v0.1.md)

### 0.8.20 — Geometry certificate and contact / Chronos gates

- Shared `CertificateStatus` (`Pass` / `Fail` / `Indeterminate` / `NotEvaluated`)
- `GeometryCertificateAPI.evaluate_tube_geometry` — \(d_\min > 2a\), \(a\kappa_\max \le 1\)
- Contact-pressure saturation; Chronos first-hitting (linear interpolation); rank-9 singular-value diagnostics
- Tests: `test_geometry_certificate.py`, `test_contact_saturation.py`, `test_chronos_first_hitting.py`, `test_rank9_diagnostics.py`

### 0.8.21 — Polygonal→smooth and Biot–Savart gates

- `PolygonalSmoothCertificateAPI` — Hausdorff / tangent / curvature bounds vs tube radius
- `BiotSavartGateAPI` — bounded-domain residual; empty regularization or zero samples → `Indeterminate` (never implicit Pass)
- Tests: `test_polygonal_smooth_certificate.py`, `test_biot_savart_gate.py`

### 0.8.22 — Operational spacetime and QSS scaffolding

- `OperationalSpacetimeAPI` — radar interval \(T_\mathrm{radar}=(T_++T_-)/2\), Lorentz boost (x and 3-vector)
- `QSSSpectroscopyAPI` — synthetic 2×2 eigenproblem and diagonal pseudospectrum; epistemic strings until 0.8.27
- QSS `conditioning` is a **deprecated alias** of `eigenvalue_magnitude_ratio` (not matrix \(\kappa\))

### 0.8.23 — Pipeline provenance

- `PipelineProvenanceAPI` — KnotPlot → Ridgerunner → smoothing → SSTcore / VortexLab
- `PipelineCertificationStatus` (`Unknown` / `Candidate` / `Certified`); SHA-256 record fingerprints
- Schema: `resources/schemas/pipeline_provenance.schema.json`

### 0.8.24 — Core–torsion mass (no factor two)

- Canonical \(M = E_0 I / c_T^2\); `torsion_inertial_mass_legacy_factor2` kept only as a regression trap
- Anisotropy residuals \(\hat\chi\), \(\delta_\mathrm{aniso}\)
- `LinkFieldGateAPI` scaffolding with failure classes E/T/N/M

### 0.8.25 — KAM stage-1 diagnostics

- `KAMDiagnosticsAPI.stage1` — frequencies, Hessian, detuning, Diophantine margin; sectors KAM-S / KAM-T
- Stages 2–5 remain scaffolding (achieved stage capped at KAM1 on Pass)
- `golden_ratio_null_test` is **not** a physical centreline constant

### 0.8.26 — Fmax provenance and \(M_0(T)\)

- `ValueOrigin` (`CanonicalSnapshot` / `Recomputed` / `CalibratedInput`)
- Fmax snapshot `29.053507` vs recompute; Rydberg \(16\pi^2\) helper; intentional \(32\pi^2\) trap
- \(M_0/m_e = L_\mathrm{tot}/4\); `rho_horn` alias of `RHO_CORE`
- Tests: `test_fmax_rydberg.py`, `test_canonical_snapshot.py`, `test_bare_mass.py`

### 0.8.27 — CheckKind and evidence export

- Closed `CheckKind` vocabulary (see [`epistemic_vocabulary.md`](epistemic_vocabulary.md))
- `EvidenceReportAPI.write_evidence_report` always stamps matching `sstcore_version` and `canon_version`
- `CertificateStatus` = gate outcome; `PipelineCertificationStatus` = chain status; `ValueOrigin` = constant provenance — do not mix

### 0.8.28 — Action–phase mass-shell clock

- \(H = \mathrm{hypot}(P c, E_0)\), \(V = P c^2 / H\), \(\gamma = H/E_0\), \(d\tau/dT = E_0/H\)
- Fixed-momentum internal phase rate \(\Omega = \Omega_0 E_0/H\)
- Residual bundle, shape-separability, fixed-\(V\) error factor
- Reuses \(M_0(T)\) from 0.8.26 and `CheckKind` from 0.8.27

### Audit remediation (on 0.8.28, before 0.8.36)

- **R1** — QSS Node binder, Linux Python link, real SHA-256, KAM \(n>2\) det, resource discovery, source-bundle manifest
- **R2** — action-phase shape/fixed-\(V\) guards, provenance validation, polygonal claim downgrade, torsion/JSON/QSS metric fixes
- **R3** — spacetime/contact/rank/Node tests/types/`list_bindings`/wheel metadata; source-bundle builder with normalized mtimes

### Knot library and resources (after 0.8.28)

- Gilbert **CanonIdeal** consolidated under `resources/ideal/`; missing knot resources **fail loudly**
- KnotPlot **relaxed ridgerunner** exports; INDEX-backed getters (`list_knotplot_ids`, `get_knotplot_ab_path`, polish/build script)
- `get_knotplot_ideal_path` / `knotplot()` are **deprecated AB shims** — not CanonIdeal
- Workbench importer tool; vendored ridgerunner tooling; curated `knots/final` geometry + VECT
- Policy: [`knot_sources.md`](knot_sources.md) — never mix ideal / KnotPlot / Fremlin for canon mass or Biot–Savart

### 0.8.29–0.8.32 — Density ontology and scaling

- \(\rho_f\) is a **2-sf calibration**, not a derived uncertainty band
- \(\rho_\mathrm{eff}\) rescale must not alter calibrated triad \((v_\mathrm{swirl},\omega_c,r_c,\Gamma_0)\)
- VAM line-inertia (kg/m) is **not** a derivation of \(\rho_f\) (kg/m³)
- Allowed energy-density forms: \(\tfrac12\rho_\mathrm{eff}|\partial_t A|^2\), \(\tfrac12 J_\omega|\omega|^2\); forbidden: \(\tfrac12\rho_f|\omega|^2\) without \(\ell^2\)
- Rotor: \(J_\omega^\mathrm{rot}=\pi r_c^2\rho_\mathrm{horn}\), \(\varphi_\mathrm{dyn}^\mathrm{ref}=\rho_\mathrm{ref}/(\pi\rho_\mathrm{horn})\), \(\ell_{\rho,\mathrm{eq}}^\mathrm{ref}=\sqrt{J_\omega^\mathrm{rot}/\rho_\mathrm{ref}}\)
- **Breaking (0.8.32):** `7.0e-7` is \(\rho_\mathrm{ref}\) **[LEGACY REFERENCE]**. New `SST::Constants::RHO_REF`. `values().rho_f` / `RHO_FLUID` still return this number for compatibility and must **not** be treated as a calibrated primitive in \(P_\mathrm{cal}\)

### 0.8.33–0.8.35 — Worldsheet, ideal regime, projector

- Two-form degree guard; \(q_B\not\equiv\Gamma_0\); \(B\not\equiv A_\mathrm{EM}\); material \(v\not\equiv A_\mathrm{eff}\)
- Compact vs slender via \(\varepsilon_\kappa\), \(\varepsilon_\mathrm{sep}\); Moffatt–Ricca \(H=\Gamma^2(\mathrm{Wr}+\mathrm{Tw})\); LIA/KAM excluded on compact ideal
- Sphere integral \(8\pi/3\); \(R_0=(8\pi/3)(L/D)\); HighRes \(L/D=16.3714672385\) vs Gilbert \(16.371637\) must not be mixed

### 0.8.36 — Maxwell stack

- `SpectroResponseAPI` — \(\Delta E\), \(\nu=\Delta E/h\), linear \(\delta\nu\); no double-count of \(H_K\) inside \(\Xi_K\)
- `MaxwellKineticAPI` — three-gate \(G\neq 0\), \(E_\mathrm{drive}\ge\Delta\), \(\tau\lesssim t_\mathrm{obs}\)
- `MechanicalFalsifierAPI` — \(\Delta p_\omega=p_\perp-p_\parallel\); \(C_\mathrm{blind}\); scaling \(\rho_f^1 v^2 L^0\)
- `SwirlTonicAPI` — Stokes circulation, material holonomy; \(A_\mathrm{st}^{(m)}\not\equiv A_\mathrm{eff}\)
- Full-probe scripts updated for the new modules; `<algorithm>` include for GCC; audit-summary tests use dynamic expected values

---

## Migration

- **Optie A** — always bump `include/sstcore_version.h`, `setup.py`, `package.json`, `src/SSTcore/__init__.py`, and Node `engineInfo()` together
- **npm** — install `sst-core`, not the old registry name
- **\(\rho_f\) / \(\rho_\mathrm{ref}\)** — keep using `values().rho_f` only as the legacy 2-sf reference; classify observables with `ScalingAuditAPI` before inferring a density pin
- **Core torsion** — use `torsion_inertial_mass`; the factor-2 helper is a forbidden regression path
- **Knot IDs** — canon mass / Biot–Savart / \(L_K\) require Gilbert `ideal.txt` (`3:1:1`, …) via `resolve_knot_ref` / `assert_canon_ideal`. KnotPlot `knot_3.1` is relaxed import unless `allow_non_canonical_geometry_for_research_only=True`
- **QSS** — prefer `eigenvalue_magnitude_ratio`; `conditioning` is a compatibility alias
- **Epistemic labels** — map pre-0.8.27 `epistemic_status` strings with `check_kind_from_export_string`

Existing positional callers of 0.8.18 resolved-tube APIs continue to work.

---

## Out of scope (still)

- Fermat-orphan / Nonrelease v0.3
- Kirchhoff–Cosserat; LIA/KAM on compact ideal trefoil as a closed fit
- EM-stiffness as a closed calibration
- Folding \(\varepsilon_\mathrm{seed}\) into \(\varepsilon_\mathrm{geom}\); field gates \(F_1\)–\(F_3\) as production certificates
- Zenodo mint/push (user-only)

---

## Test checklist

```powershell
pytest tests/test_version_consistency.py tests/test_canon_v0_8_12_alignment.py -q
pytest tests/test_geometry_certificate.py tests/test_polygonal_smooth_certificate.py tests/test_biot_savart_gate.py -q
pytest tests/test_operational_spacetime.py tests/test_qss_spectroscopy.py tests/test_pipeline_provenance.py -q
pytest tests/test_core_torsion.py tests/test_kam_diagnostics.py tests/test_action_phase.py -q
pytest tests/test_canon_v0_8_29_32_ontology.py tests/test_canon_v0_8_33_36_modules.py -q
npm test
python scripts/gen_binding_manifest.py --check
python examples/example_density_ontology.py
python examples/example_maxwell_canon.py
python SSTcore_full_probe.py
```

---

## Summary

**SSTcore v0.8.36** is the recommended PyPI / npm / source bundle since v0.8.18: Canon 0.8.19–0.8.36 is bound in C++, Python, and Node; knot sources are role-separated; \(\rho_\mathrm{ref}=7\times10^{-7}\) is labeled legacy; Maxwell-stack diagnostics are available as research gates, not closed physics claims.
