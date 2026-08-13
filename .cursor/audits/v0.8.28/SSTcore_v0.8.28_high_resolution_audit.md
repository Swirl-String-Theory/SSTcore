# SSTcore v0.8.28 — High-resolution source, build and mathematical audit

**Audited artifact:** `SSTcore-source-bundle-0.8.28.zip`  
**SHA-256:** `8bb4a575456d771f546f579a05538ca189948b17882d010061e0b107f4418168`  
**Inventory:** 9,806 files, 308 directories, 448.81 MiB extracted  
**Audit date:** 2026-07-29T01:26:44.260418+00:00  
**Methods:** source inspection, CMake builds, native tests, Python tests, package/Node wiring review and adversarial numerical probes.

## Executive verdict

\[
\boxed{\text{NOT RELEASE-READY AS A SELF-CONTAINED SOURCE/NPM BUNDLE}}
\]

\[
\boxed{\text{NATIVE CORE AND MOST PYTHON FORMULAS ARE SUBSTANTIAL, BUT MAJOR PATCHES ARE REQUIRED}}
\]

The result is not a failed implementation. The upgrade contains substantial working code: versions are synchronized, the native core builds, three C++ executables pass, and—after an audit-only Python link correction plus an explicit resource path—**139 Python tests pass with 25 skips**.

Five blockers remain: incomplete archive contents, absent Node QSS binder, broken Linux Python CMake linking, false SHA-256 provenance naming/behavior, and a KAM n>2 false-positive path.

## Results at a glance

| Category | Result |
|---|---:|
| Blockers | 5 |
| High-priority defects | 8 |
| Medium-priority defects | 6 |
| Positive verified findings | 4 |
| Native C++ tests | **3/3 passed** |
| Full shipped pytest collection | blocked by 3 absent helper modules |
| Reduced pytest, no resource override | 125 passed, 33 skipped, 6 failed |
| Reduced pytest, correct resource path | **139 passed, 25 skipped** |
| Node build/test | not runnable from delivered archive; static wiring blocker also found |
| Wheel | not established; audit run did not complete |

## Build and release-engineering findings

### Native C++ core

The static library built successfully with Python disabled. `test_frenet`, `test_sst_integrator` and `test_resolved_tube_geometry` all returned exit code 0.

### Source-bundle completeness

`package.json` references `scripts/`, `lib/resource_helpers`, `README.md`, `LICENSE`, `dist/` and `prebuilds/`; these are absent. Missing `scripts/` also causes pytest collection errors for `audit_binding_examples`, `binding_inventory` and `source_zip_common`.

### Python CMake build

The original CMake links the extension only to `sstcore_lib` and adds `-Wl,--no-undefined`. That produced unresolved Python symbols. An audit-only `Python::Python` link allowed the module to build; this is evidence for the fix, not a modification to the uploaded ZIP.

### Node wiring

`module_node.cpp` declares and invokes `bind_qss_spectroscopy`, but no `qss_spectroscopy_node.cpp` exists and the CMake Node source list omits it. The capability is nevertheless advertised.

### Resource lookup

`src/SSTcore/__init__.py` checks `src/resources` rather than repository-root `resources`. Six tests fail without `SSTCORE_RESOURCES`; with the correct path the reduced suite reaches 139 passed / 25 skipped.

### Wheel status

A wheel build was attempted after supplying local pybind11 files. It spent the audit window generating/compiling a large embedded-resource surface and did not complete. This audit therefore does not claim either a passing or definitively failing final wheel.

## Mathematical and API findings

### Action–phase mass-shell

Implemented correctly in the ordinary domain:

\[
H=\operatorname{hypot}(Pc,E_0),\qquad
V=\frac{Pc^2}{H},\qquad
\gamma=\frac{H}{E_0},\qquad
\frac{d\tau}{dT}=\frac{E_0}{H},\qquad
\Omega=\Omega_0\frac{E_0}{H}.
\]

Missing: `delta_shape_separability`, the coupled momentum–shape countermodel, and the fixed-V error guard. Residuals are absolute and dimensionful, and large finite inputs can overflow intermediate products.

### KAM stage-1

For \(n>2\), the implementation uses the product of diagonal Hessian entries as a determinant proxy. The singular matrix

\[
D=\begin{pmatrix}1&1&0\\1&1&0\\0&0&1\end{pmatrix},\qquad \det D=0,
\]

was reported as determinant 1 and `Pass/KAM1`. This must be treated as a release blocker.

### Provenance

Fields named `*_sha256` accept arbitrary strings and are generated with 64-bit FNV-1a. Stages need only be non-decreasing, timestamps are not validated, and malformed records were certified in an adversarial probe.

### Polygonal-to-smooth certification

The current sampled distances/tangent errors and curvature-radius check are useful diagnostics, but they do not prove continuous Hausdorff bounds, reach/thickness or ambient isotopy. `Pass` overstates the mathematical result.

### Core torsion

The corrected formula \(M_{\rm torsion}=E_0I/c_T^2\) is present. However, `dimensional_residual` is fixed at zero and the anisotropy calculation ignores the lower matrix triangle.

### Evidence export

CheckKind is a good addition. The manual JSON writer can nevertheless emit invalid JSON for control characters and NaN/Inf, and it loses numeric precision.

### QSS

The field called `conditioning` is only an eigenvalue-magnitude ratio. A defective matrix with a huge off-diagonal returned conditioning 1, so the name and interpretation are mathematically wrong.

### Operational spacetime

The radar and x-axis boost formulas are broadly correct. The implementation lacks arbitrary-direction boosts and normalizes the invariant residual with `abs(s2)+1.0`, which is unit-dependent.

## Deelplan compliance matrix

| Deelplan | Status | Assessment |
|---|---|---|
| 0 / 0.8.19 | **PARTIAL** | Version sync is complete, but the archive cannot execute its full documented CI and omits the planned management/coverage documents. |
| 0.8.20 | **PARTIAL** | Geometry/contact/Chronos APIs exist; threshold semantics and rank-conditioning need strengthening. |
| 0.8.21 | **PARTIAL / OVERCLAIM** | Biot and polygonal-smooth gates exist, but current evidence is diagnostic rather than rigorous certification. |
| 0.8.22 | **PARTIAL** | Spacetime/QSS scaffolding exists; QSS Node wiring is absent and conditioning is misnamed. |
| 0.8.23 | **FAILS CORE CONTRACT** | Provenance records exist, but SHA-256, canonical serialization, strict continuity and validation are not implemented. |
| 0.8.24 | **PARTIAL** | The factor-2-free formula exists; tensor/residual validation is incomplete. |
| 0.8.25 | **FAILS MATHEMATICAL GUARD** | The n>2 KAM proxy can falsely return Pass. |
| 0.8.26 | **MOSTLY IMPLEMENTED** | Snapshot/recompute separation, density metadata and M0 helpers exist; precision/package semantics need refinement. |
| 0.8.27 | **PARTIAL** | CheckKind/evidence exist, but JSON robustness, schema and parity are incomplete. |
| 0.8.28 | **PARTIAL** | Core formulas exist; the discriminating shape/fixed-V/countermodel guards are absent. |

## Full finding ledger

| ID | Severity | Area | Finding | Required action |
|---|---|---|---|---|
| B-001 | **BLOCKER** | Bundle completeness | The source bundle omits scripts/, lib/, docs/, README.md, LICENSE, dist/ and prebuilds/ although package.json and tests reference them. | Regenerate the archive from a checked manifest and fail CI on missing referenced paths. |
| B-002 | **BLOCKER** | Node QSS wiring | src/module_node.cpp declares/calls bind_qss_spectroscopy, but qss_spectroscopy_node.cpp does not exist and is absent from the CMake Node source list. | Add and wire the binder, or remove the Node capability until it exists. |
| B-003 | **BLOCKER** | Python CMake link | The original Linux CMake build combines -Wl,--no-undefined with a Python extension that is not linked to Python::Python, producing unresolved Py* symbols. | Link Python::Python when using that linker guard, or adopt an extension-appropriate platform policy. |
| B-004 | **BLOCKER** | Provenance hash contract | APIs and fields named SHA-256 use 64-bit FNV-1a; geometry hashes use raw native double bytes. | Implement real SHA-256 over canonical serialization and validate 64-hex fields. |
| B-005 | **BLOCKER** | KAM false positive | For n>2, Hessian 'determinant' is the product of diagonal entries. A singular 3x3 Hessian was returned as determinant=1 and Pass/KAM1. | Use LU/QR/SVD rank and non-degeneracy diagnostics; return Indeterminate when a rigorous result is unavailable. |
| H-001 | **HIGH** | Action-phase completeness | Mass-shell, V, gamma, proper-time and fixed-P phase are present, but delta_shape_separability, the coupled countermodel and fixed-V gamma^2-1 guard are missing. | Implement the planned discriminating residuals and regression tests. |
| H-002 | **HIGH** | Action-phase stability | P*c, P*c*c and absolute dimensionful residuals can overflow even for finite inputs; ok only means residuals are finite. | Scale arithmetic, use V=c*((P*c)/H), normalize residuals and separate finite/valid/tolerance status. |
| H-003 | **HIGH** | Provenance certification validation | Only non-empty strings are checked; malformed hashes/timestamps and skipped stages can be certified. | Validate hash/timestamp formats, exact stage transitions and coordinate/scale compatibility. |
| H-004 | **HIGH** | Polygonal-smooth overclaim | Sampled distances, index-paired tangents and curvature radius alone are reported as a Pass certificate without reach/self-distance/isotopy bounds. | Rename current output Diagnostic/Candidate and reserve Pass for rigorous topology/thickness guards. |
| H-005 | **HIGH** | Core torsion anisotropy | dimensional_residual is hard-coded zero; anisotropy ignores the lower matrix triangle and does not validate symmetry. | Validate/symmetrize the tensor, include all entries and define a real dimensionless diagnostic. |
| H-006 | **HIGH** | Evidence JSON | Manual serialization can emit invalid JSON for control characters and NaN/Inf, and default precision is lossy. | Use a JSON library, reject/encode non-finite values, set full precision and add schema/version/input hashes. |
| H-007 | **HIGH** | QSS conditioning | The field conditioning is an eigenvalue-magnitude ratio, not eigenproblem conditioning; a defective matrix returned conditioning=1. | Rename the metric and add left/right eigenvector or resolvent-based conditioning with normalized residuals. |
| H-008 | **HIGH** | Python resource discovery | Source-checkout lookup resolves to src/resources rather than repository-root resources; six tests fail without SSTCORE_RESOURCES. | Add a correct repository-root path and test clean editable/source checkouts. |
| M-001 | **MEDIUM** | Operational spacetime | Only x-axis boosts exist and invariant residual divides by abs(s2)+1.0, introducing an undeclared unit scale. | Add arbitrary-direction boosts and dimensionally consistent normalization. |
| M-002 | **MEDIUM** | Contact/rank diagnostics | One epsilon mixes pressure and dimensionless ratio tolerances; negative pressures are accepted; rank-9 Pass lacks a conditioning ceiling. | Separate tolerances, validate domains and gate on conditioning. |
| M-003 | **MEDIUM** | Node tests/types | npm test runs only test_basic.js; new module tests are not part of the default command; index.d.ts largely hides gaps behind an index signature. | Use a unified Node test runner and explicitly type the new APIs. |
| M-004 | **MEDIUM** | Binding introspection | list_bindings reports 291 functions and 0 classes, misclassifying pybind classes. | Use PyType_Check or equivalent and add expected-class tests. |
| M-005 | **MEDIUM** | Wheel/package configuration | The wheel audit did not finish; it exposed stale py_modules, ambiguous resource package discovery and deprecated license metadata. | Clean package discovery/metadata and pre-generate or cache embedded resources. |
| M-006 | **MEDIUM** | Archive timestamps | Future mtimes triggered unnecessary CMake rebuild behavior. | Normalize archive mtimes for reproducible builds. |
| P-001 | **POSITIVE** | Version synchronization | package.json, setup.py, Python __version__ and sstcore_version.h agree on 0.8.28. | Keep the version guard. |
| P-002 | **POSITIVE** | Native core | The static C++ library builds and test_frenet, test_sst_integrator and test_resolved_tube_geometry all pass. | Preserve these as mandatory CI gates. |
| P-003 | **POSITIVE** | Python regression surface | With an audit-only CMake link fix and correct resource path, 139 tests pass and 25 skip. | Use this as the remediation baseline. |
| P-004 | **POSITIVE** | Upgrade breadth | The planned C++/Python modules for 0.8.20 through 0.8.28 are substantially present. | Focus next work on rigor, bindings and release completeness rather than rewriting. |

## Prioritized repair programme

### Patch set A — release blockers

1. Restore all omitted archive paths and add manifest-completeness CI.
2. Add/wire the QSS Node binder or remove its advertised capability.
3. Correct Linux Python-extension linking.
4. Replace FNV implementations exposed as SHA-256 with canonical true SHA-256.
5. Replace the KAM n>2 proxy with LU/QR/SVD diagnostics.

### Patch set B — scientific guards

6. Complete action–phase shape-separability, coupled-countermodel and fixed-V tests.
7. Downgrade polygonal-smooth Pass until reach/isotopy bounds exist.
8. Correct anisotropy tensor handling and dimensional diagnostics.
9. Replace or rename QSS conditioning.
10. Normalize residuals and attach explicit tolerances/statuses.

### Patch set C — evidence and product quality

11. Use a standards-compliant JSON library/schema.
12. Repair source-checkout resource discovery.
13. Integrate every new Node test in the default command.
14. Complete TypeScript declarations.
15. Normalize archive timestamps and harden wheel/resource generation.

## Release recommendation

Do not publish this exact ZIP as the final canonical v0.8.28 source/NPM artifact. A defensible label is:

\[
\boxed{\texttt{v0.8.28-rc1 — feature-complete candidate, audit remediation required}}
\]

After blocker remediation, rerun native C++, full pytest without exclusions or environment overrides, Node build/test/parity/pack, wheel build plus clean-venv import, and the adversarial KAM/provenance/action-phase/evidence tests.

## Evidence note

The accompanying evidence archive contains the build/test logs, adversarial probe output and the audit-only CMake patch. The original uploaded ZIP was not modified.