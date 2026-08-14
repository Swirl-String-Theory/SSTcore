# ⚙️ SSTcore

**Hybrid C++ / Python / Node engine for Swirl–String Theory**

> If spacetime can bend, why shouldn’t it knot?

Welcome to **SSTcore** — the computational backbone of the SST programme.  
A shared C++23 numeric core, exposed through **pybind11** (`pip install SSTcore`) and **Node N-API** (`npm install sst-core`), built so that stiff vortex, knot, and field calculations can run roughly **10–100×** faster than pure Python while still feeling like a Python (or TypeScript) library.

**Package ≡ Canon version:** **v0.8.36**  
(`SSTCORE_VERSION` ≡ `SSTCORE_CANON_VERSION` — Optie A)

Chat the Canon that this engine implements:  
[Gemini notebook — Canon v0.8.36](https://notebook.google.com/notebook/7264029f-6bef-4720-be02-a0ad7b8cddb4)

---

## 🧭 Place in the workshop

| Repository | Role |
|------------|------|
| [Swirl-String-Theory](https://github.com/Swirl-String-Theory/Swirl-String-Theory) | Papers, **SST-CANON**, provenance notebooks, Zenodo canon |
| **SSTcore** (this repo) | Stable C++/Python/Node API — `pip install SSTcore`, `npm install sst-core` |
| [SST-Workbench](https://github.com/Swirl-String-Theory/SST-Workbench) | Falsifiers, KnotPlot→Ridgerunner intake, dashboards, research packs |

Theory lives in the Canon. Numbers live here. Bruises live in the Workbench.

---

## 💾 What it computes

SSTcore is not a generic CFD toy. It is the engineered substrate for SST’s knot / filament / fluid / clock / Maxwell-bridge programme:

- **Knot & filament kernels** — Biot–Savart, Frenet helicity, vortex rings, ideal Gilbert catalogs, Fourier-series (`.fseries`) curves
- **Geometry certificates** — tube metrics, polygonal→smooth bounds, contact saturation, Chronos first-hitting, Biot residual gates
- **Pipeline provenance** — KnotPlot → Ridgerunner → SSTcore/VortexLab certification chain (`PipelineProvenanceAPI`)
- **Mass-shell & clocks** — action–phase API (\(H\), \(V\), \(\gamma\), \(d\tau/dT\), \(\Omega\)), core torsion / link-field gates
- **Density / rotor / scaling** — \(\rho_{\mathrm{sub}}\) / \(\rho_{\mathrm{eff}}\), rotor participation, \(\rho_{\mathrm{ref}}\) audits
- **Maxwell-stack diagnostics (v0.8.36)** — swirl-tonic (material velocity as vorticity-potential), kinetic closure, Stokes/holonomy falsifier hooks — **not** to be conflated with the independent transverse / link field \(\mathbf{A}_{\mathrm{eff}}\)
- **Bundled resources** — `resources/ideal/`, `Knots_FourierSeries/`, KnotPlot `INDEX.json` + AB-XML

EM-field evolution and GR-vs-SST time-dilation comparisons remain available as bridge tools; the headliner since 0.8.19 is the **canon API ladder**.

WASM / browser: there is a **stub** path. It is **not** a production Angular product yet. Prefer native Python or Node.

---

## 🪜 Canon API ladder (v0.8.19 → v0.8.36)

This *is* the product. Each rung is a C++ module with Python and (usually) Node bindings, plus paired `examples/example_*.py` / `examples/example_*.ts`.

| Version | Module / change | Role |
|---------|-----------------|------|
| 0.8.19 | Optie A sync + smooth-tube metrics | Package ≡ canon; equilateral max-dev; `GEOMETRY_CERTIFICATE_PROTOCOL_v0.1` |
| 0.8.20 | `GeometryCertificateAPI` | Tube geometry, contact saturation, Chronos first-hitting, rank-9 |
| 0.8.21 | `PolygonalSmoothCertificateAPI` + `BiotSavartGateAPI` | Polygonal→smooth bounds; bounded-domain Biot residual |
| 0.8.22 | `OperationalSpacetimeAPI` + `QSSSpectroscopyAPI` | Radar/Lorentz; synthetic QSS eigen/pseudospectrum |
| 0.8.23 | `PipelineProvenanceAPI` | KnotPlot→Ridgerunner→SSTcore chain |
| 0.8.24 | `CoreTorsionAPI` + `LinkFieldGateAPI` | \(M = E_0 I / c_T^2\); link-gate E/T/N/M |
| 0.8.25 | `KAMDiagnosticsAPI` | KAM-S/T stage-1; golden-ratio null-test only |
| 0.8.26 | `ValueOriginAPI` + \(M_0(T)\) | Fmax snapshot vs recompute; Rydberg \(16\pi^2\) |
| 0.8.27 | `CheckKind` + `EvidenceReportAPI` | Epistemic export vocabulary |
| 0.8.28 | `ActionPhaseAPI` | Mass-shell clock |
| 0.8.29 | `ValueOriginAPI` guards | \(\rho_f\) provenance; VAM no-go |
| 0.8.30 | `DensityOntologyAPI` | \(\rho_{\mathrm{sub}}\) / \(\rho_{\mathrm{eff}}\) / \(J_\omega\) / \(\mu_\ell\) |
| 0.8.31 | `RotorParticipationAPI` | Rotational participation; twist vs Kelvin bend |
| 0.8.32 | `ScalingAuditAPI` | \(\rho_{\mathrm{ref}}\) legacy; \(P_{\mathrm{cal}}\) / \(P_{\mathrm{open}}\) / \(P_{\mathrm{ref}}\) |
| 0.8.33 | `WorldsheetGuardsAPI` | Form-degree / non-identification guards |
| 0.8.34 | `IdealKnotRegimeAPI` | \(\varepsilon_\kappa\), \(\varepsilon_{\mathrm{sep}}\); Moffatt–Ricca; LIA/KAM exclusion |
| 0.8.35 | `TransverseProjectorAPI` | \(8\pi/3\), \(R_0\), \(R_{\mathrm{SST}}\); HighRes vs Gilbert |
| **0.8.36** | spectro / kinetic / falsifier / **swirl-tonic** | Maxwell-stack diagnostics |

Full notes: [`docs/RELEASE_NOTES_0.8.36.md`](docs/RELEASE_NOTES_0.8.36.md) · Coverage matrix: [`docs/BINDING_COVERAGE.md`](docs/BINDING_COVERAGE.md)

---

## 🚀 Install

Same Canon core, two first-class installs:

| Surface | Command | Package name |
|---------|---------|--------------|
| **Python** | `pip install SSTcore` | `SSTcore` (PyPI) |
| **Node.js** | `npm install sst-core` | `sst-core` (npm — note the **hyphen**) |

### Python (PyPI name: `SSTcore`)

```bash
pip install SSTcore
python -c "import SSTcore; print(SSTcore.__version__, SSTcore.CANON_VERSION)"
```

Preferred import:

```python
import SSTcore
from SSTcore import get_resources_dir, get_ideal_txt_path
```

Legacy shim `import sstcore` may still resolve; prefer **`SSTcore`**.  
Requires Python ≥ 3.9; wheels ship native `_native` extensions + resources.

### Node.js (npm name: `sst-core`)

```bash
npm install sst-core
node -e "const sst=require('sst-core'); console.log(sst)"
```

Native N-API addon (`sstcore.node`) + TypeScript examples under `examples/example_*.ts`.  
Details: [`docs/README_NPM.md`](docs/README_NPM.md) · Build notes: [`NODE_BUILD.md`](NODE_BUILD.md)

### From source

```bash
# Python (needs a C++ toolchain; see CONTRIBUTING.md for Windows MSVC / AutoRun pitfalls)
git submodule update --init --recursive   # if needed for extern/pybind11
pip install .
# or editable:
pip install -e .

# Node addon
npm run build:node
```

CMake remains available for IDE workflows (CLion / Visual Studio / Clang):

```bash
cmake -S . -B build
cmake --build build --config Release
```

Deep Windows / wheel / packaging rules: [`CONTRIBUTING.md`](CONTRIBUTING.md)

If you received a **source ZIP** (`SSTcore_source_v0.x.x.zip`) rather than a PyPI wheel, unpack nested resource archives first:

```bash
python scripts/unpack_source_resources.py
pip install -e .
python -m pytest tests/ -q
```

See [`resources/README.md`](resources/README.md).

---

## 📦 Resources API

After `pip install`, knot catalogs and ideal databases resolve through the package:

```python
from SSTcore import (
    get_resources_dir,
    get_knots_fourier_series_dir,
    get_ideal_txt_path,
    get_knotplot_ab_path,
    list_knotplot_ids,
)

resources_dir = get_resources_dir()
kfs_dir = get_knots_fourier_series_dir()
ideal_path = get_ideal_txt_path()          # resources/ideal/ first, flat legacy second
ab_path = get_knotplot_ab_path("knot_3.1") # INDEX-backed AB-XML
kp_ids = list_knotplot_ids()
```

- Gilbert ideal data lives under **`resources/ideal/`**
- KnotPlot entities under **`resources/knotplot/`** (INDEX.json); prefer `get_knotplot_ab_path` over deprecated helpers
- Override root with env var **`SSTCORE_RESOURCES`**
- Repo-only Ridgerunner tooling: `tools/knotplot/` (not packaged in the wheel)

More: [`resources/README.md`](resources/README.md)

---

## 🧪 Examples & tests

Paired demos:

```text
examples/example_biot_savart.py
examples/example_biot_savart.ts
```

```bash
# Python suite
python -m pytest tests/ -q

# Node
npm test
npm run test:parity
npm run examples:node:all   # after npm run build:node
```

Mapping table (binding → TS → Python): [`examples/README.md`](examples/README.md)

Minimal Python smoke:

```python
from SSTcore import get_ideal_txt_path, get_resources_dir

print(get_resources_dir())
print(get_ideal_txt_path())
```

Canon chat while you code:  
[Gemini notebook — Canon v0.8.36](https://notebook.google.com/notebook/7264029f-6bef-4720-be02-a0ad7b8cddb4)

---

## 📂 Layout today

```text
SSTcore/
├── src/                      # C++ core + *_py.cpp / *_node.cpp + Python package
│   ├── SSTcore/              # Python package (__init__.py, catalogs, CLI)
│   ├── module_sst.cpp        # pybind entry
│   ├── module_node.cpp       # N-API entry
│   ├── wasm/                 # stub — not production
│   └── curve|filament|knot|tube|… domains
├── include/                  # public headers + sstcore_version.h
├── resources/                # ideal/, Knots_FourierSeries/, knotplot/, schemas/
├── examples/                 # example_*.py + example_*.ts
├── tests/
├── docs/                     # BINDING_COVERAGE, README_NPM, release notes
├── scripts/, cmake/, tools/, extern/pybind11
├── CMakeLists.txt, setup.py, pyproject.toml, package.json, binding.gyp
├── index.js, index.d.ts, NODE_BUILD.md, LICENSE, Readme.md
```

Bindings live **next to** the C++ sources under `src/` — there is no separate `src_bindings/` tree.

---

## 🧬 Provenance (short)

SST did not begin as a hydrodynamics package. Notebooks from **2012** and a **2013** proto-canon asked impedance–resonance questions; vorticity and knots arrived later as the dynamical language. The engine you are looking at is the 2026 computational face of that programme.

- [2013 Hypotheses on Constants in Quantum Mechanics, using Classical Logic](https://docs.google.com/document/d/1YjhB4Z01CNf3p-W_sCDBcsK4tHlXZnmRRS5NOFviIH8/edit?usp=sharing) (`DOC2013-CANON-001` — first canon attempt)
- [Fundamental considerations for the theory of the liquid æther](https://docs.google.com/document/d/1PZpK9MFv8t3XsWils4dxlhmRndhp5tNygtDXByGUdH0/edit?usp=sharing) (last VAM draft; historical)
- Scanned notebooks: see the [org README](https://github.com/Swirl-String-Theory/Swirl-String-Theory#origin-2012--now) (`docs/Notebook-2012.pdf` … `Notebook-2015.pdf`)

Geometry certification provenance in the Workbench: KnotPlot → Ridgerunner → SSTcore (`PROJ2026-KNOTPLOT-RR-001`).

---

## 📖 Documentation

| Doc | Contents |
|-----|----------|
| [`docs/BINDING_COVERAGE.md`](docs/BINDING_COVERAGE.md) | C++ / Python / Node matrix |
| [`examples/README.md`](examples/README.md) | Paired demo map |
| [`resources/README.md`](resources/README.md) | Ideal / f-series / knotplot / source-ZIP unpack |
| [`docs/README_NPM.md`](docs/README_NPM.md) | npm `sst-core` usage |
| [`docs/RELEASE_NOTES_0.8.36.md`](docs/RELEASE_NOTES_0.8.36.md) | Ladder + changelog |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Packaging & Windows build traps |
| [`NODE_BUILD.md`](NODE_BUILD.md) | Native addon build |

---

## 🔬 Author

**Omar Iskandarani**  
Independent Researcher, Groningen, The Netherlands  
ORCID: [0009-0006-1686-3961](https://orcid.org/0009-0006-1686-3961)  
Email: `info@omariskandarani.com`

Conceived, written, and (sometimes reluctantly) coded — then pushed into C++ so the æther would stop timing out.

---

## 🧃 Warning

This software may cause:

- vortex-based worldview shifts,
- sudden suspicion of bare spacetime curvature,
- hallucinations of swirling field lines in your breakfast cereal,
- an urge to certify every trefoil before coffee.

Proceed responsibly.

---

## 💬 Contact

Open an [issue](https://github.com/Swirl-String-Theory/SSTcore/issues), whisper into the æther, or start from the Canon chat above.  
This code is listening. Always.

---

## License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)  
© 2012–2026 Omar Iskandarani.

Educational and research use welcome. Commercial reuse requires permission.

Package citation (Zenodo): `10.5281/zenodo.19683034`  
Canon edition (Zenodo): [10.5281/zenodo.21922231](https://doi.org/10.5281/zenodo.21922231)
