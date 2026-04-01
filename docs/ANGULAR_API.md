# SSTcore native API — Angular / Node backend

The npm package exposes a **single native addon** (`sstcore.node`) loaded by [index.js](https://github.com/Swirl-String-Theory/SSTcore/blob/master/index.js). The **browser** does not load `.node`; use a **Node** server (Nest, Express, etc.) and call the addon from route handlers.

## Priority surface (typical dashboard / physics UI)

| Area | Exports (examples) | Notes |
|------|-------------------|--------|
| Biot–Savart / grids | `computeVelocity`, `computeVorticity`, `biotSavartVelocity`, … | Filaments + regular grids |
| F-series / helicity | `computeHelicityFromFseries`, `canonicalizeFseriesFileInplace`, … | Paths on server filesystem |
| Knot / topology | `computeWrithe`, `computeLinkingNumber`, `parseFseriesMulti`, … | See `knot*` exports |
| Ab-initio mass | `ParticleEvaluator` class, `zooEvaluateAllGoldenNls` | Heavy relaxation on server |
| SST mass | `computeSstMass` | Closed polyline → `(m_core, m_fluid)` |

## Full export discovery

After `require('SSTcore')` (or local `index.js`), call **`listBindings()`** — returns `{ functions, classes, attributes, counts }` (same idea as Python `list_bindings`).

## TypeScript

Use [index.d.ts](../index.d.ts). Run per-domain demos under [node_examples/](../node_examples/) (see `node_examples/README.md`).

## Dashboard bridge (optional)

Use `node_examples/*.example.ts` as the **contract** for HTTP request/response shapes when wiring an Angular app to your Node API.
