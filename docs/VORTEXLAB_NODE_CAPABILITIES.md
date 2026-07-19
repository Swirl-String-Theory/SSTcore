# VortexLab ↔ SSTcore Node capabilities

This document maps VortexLab needs to existing SSTcore surfaces.  
**No JavaScript re-implementation of missing C++ kernels.** Missing Node items need thin N-API wrappers around existing C++ (or new C++ work first).

For the full per-module C++ / Python / Node file matrix, see [`BINDING_COVERAGE.md`](BINDING_COVERAGE.md).

Legend: **Y** present · **P** partial/proxy · **W** wrapper needed (C++ exists) · **N** new C++ needed · **—** absent

| Capability | C++ | Python | Node | Notes |
|------------|-----|--------|------|-------|
| Curve sampling (fseries / Fourier eval) | Y | Y | Y | `evaluateFourierBlock`, `sampleCurveCentered`, `loadKnot` |
| Biot–Savart velocity | Y | Y | Y | `computeVelocity`, `biotSavartVelocity[Grid]` |
| Velocity reconstruction (field kernels) | Y | Y | Y | `biotSavartWireGrid`, knot grid helpers |
| RK4 / integration | Y | Y | Y | `rk4Integrate`, `evolveVortexKnot` |
| Topology clearance | — (VortexLab JS) | — | — | **N** (or keep in VortexLab); not in SSTcore C++ today |
| Gauss linking | Y | Y | Y | `computeLinkingNumber` |
| Writhe | Y | Y | P | Node: `computeWrithe`; Python also has `writhe_gauss_curve` — **W** for Gauss form |
| Frenet / helicity | Y | Y | Y | `computeFrenetFrames`, `computeHelicity`, … |
| Continuous curvature | Y | Y | P | Node discrete via Frenet/`loadKnot`; exact Fourier curvature — **W** (`curvature_exact`) |
| Self-DCSD | Y (tube) | Y (`ResolvedTubeGeometry`) | — | **W** around `include/sst/tube/` |
| Inter-component distance | Y | Y (tube + extensions) | P | Node: `minNonNeighborDistanceFromFseries` (single curve); multi-component — **W** |
| Reach | Y | Y | P | Node: `reachProxyFromFseries`; tube `reach_rad` — **W** |
| Magnus integrator | Y | Y | Y | `createMagnusBernoulliIntegrator`, … |
| SST mass integrator | Y | Y | Y | `computeSstMass` |
| Resolved tube / tighten | Y | Y | — | **W** (large surface; not in recovery scope) |

## Directly usable for VortexLab (Node today)

- Curve sampling from embedded / fseries inputs  
- Biot–Savart and grid velocity  
- Frenet frames, helicity, RK4 filament evolution  
- Writhe / linking / twist (discrete curve forms)  
- Reach proxy and min non-neighbor distance from fseries  
- Magnus + SST mass helpers  
- **Knot catalog JS** (VortexLab-compatible): `resources/knots_data_{ideal,fourier,knotplot}.js` via `resources/load_knot_catalogs.js`

### Knot catalog JS (Node)

VortexLab loads these as browser `<script>` files. In Node/TS use the loader (does not attach catalogs to `require('sst-core')`):

```js
// CommonJS (published package)
const { loadIdealCatalog, loadFseriesCatalog, loadKnotplotCatalog } =
  require('sst-core/resources/load_knot_catalogs');

const ideal = loadIdealCatalog();
console.log(ideal.ids.length, ideal.db['3:1:1']);
```

```ts
// TypeScript / tsx (repo checkout)
import {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
} from '../resources/load_knot_catalogs';

const fseries = loadFseriesCatalog();
const entry = fseries.db['3_1'];
```

Example: `npm run example:knot-catalogs` → [`examples/example_knot_catalogs.ts`](../examples/example_knot_catalogs.ts).

The Node full probe (`SSTcore_full_probe.js`) loads all three catalogs and reports `js_catalog` summaries (id counts + sample hits; never dumps coefficients).

Workbench/VortexLab HTML may still reference older filenames (`ideal_knots_data.js`, …) until those trees are synced.

### Python-parity resource helpers (Node)

The following Python package helpers are also on `require('sst-core')` via [`lib/resource_helpers.js`](../lib/resource_helpers.js) (camelCase + snake_case):

`get_resources_dir`, `get_ideal_txt_path`, `get_knots_fourier_series_dir`, `get_knotplot_dir`, `get_ideal_ab`, `get_ideal_link`, `list_ideal_source_files`, `list_embedded_fseries_ids`, `load_fseries_knot`, `knotplot`, `resolve_knot_ref`

```js
const sst = require('sst-core');
console.log(sst.get_resources_dir());
console.log(sst.get_ideal_ab('3:1:1')?.slice(0, 60));
console.log(sst.resolve_knot_ref('3:1:1')?.ropelength);
```

`get_knotplot_dir` / `knotplot` return a path or file text when `resources/knotplot/` is present (dev checkout); published npm packs omit that large tree, so those may be `null`.

## Needs wrapper only (C++ already in `sstcore_lib`)

- Exact / continuous Fourier curvature  
- Gauss writhe variant  
- Resolved-tube DCSD, `reach_rad`, segment–segment multi-component gaps  

## Needs new C++ (or stays in VortexLab JS)

- Named **topology clearance** guard as used in VortexLab HTML  

## Policy

Do not copy VortexLab algorithms into TypeScript/JavaScript when the numeric path belongs in `sstcore_lib`. Prefer N-API binds that call the same functions Python already uses.
