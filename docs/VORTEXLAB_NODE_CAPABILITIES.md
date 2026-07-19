# VortexLab ↔ SSTcore Node capabilities

This document maps VortexLab needs to existing SSTcore surfaces.  
**No JavaScript re-implementation of missing C++ kernels.** Missing Node items need thin N-API wrappers around existing C++ (or new C++ work first).

For the full per-module C++ / Python / Node file matrix, see [`BINDING_COVERAGE.md`](BINDING_COVERAGE.md).  
Migration tracking: [`VORTEXLAB_KERNEL_STATUS.md`](VORTEXLAB_KERNEL_STATUS.md), [`VORTEXLAB_KERNEL_IMPLEMENTATION_PLAN.md`](VORTEXLAB_KERNEL_IMPLEMENTATION_PLAN.md).

Legend: **Y** present · **P** partial/proxy · **W** wrapper needed (C++ exists) · **N** new C++ needed · **—** absent

| Capability | C++ | Python | Node | Notes |
|------------|-----|--------|------|-------|
| Curve sampling (fseries / Fourier eval) | Y | Y | Y | `evaluateFourierBlock`, `sampleCurveCentered`, `loadKnot`; plus VortexLab `sampleCurve` / `resampleClosedCurve` |
| Biot–Savart velocity | Y | Y | Y | primitives; VortexLab RHS via `FilamentVelocitySolver` |
| Velocity reconstruction (field kernels) | Y | Y | Y | `biotSavartWireGrid`, knot grid helpers |
| RK4 / integration | Y | Y | Y | Frenet `rk4Integrate`; VortexLab multi-filament via `FilamentIntegrator` |
| Topology clearance / guard | Y (migration) | Y | Y | `TopologyGuard` — not reconnect |
| Gauss linking (legacy) | Y | Y | Y | `computeLinkingNumber` |
| Exact polygonal Gauss | Y (migration) | Y | Y | `computePolygonalGauss` (signed + absolute) |
| Writhe | Y | Y | Y | `computeWrithe`, `writheGaussCurve` |
| Frenet / helicity | Y | Y | Y | `computeFrenetFrames`, `computeHelicity`, … |
| Continuous curvature / reach | Y (migration) | Y | Y | `computeContinuousReach` (capability gated) |
| Self-DCSD / tube | Y | Y | Y | `ResolvedTubeGeometry` via `geometry_node.cpp` |
| Inter-component distance | Y | Y | Y | tube multi + continuous reach |
| Magnus integrator | Y | Y | Y | |
| SST mass integrator | Y | Y | Y | |
| Resolved tube / tighten | Y | Y | Y | Node: `ResolvedTubeGeometry` class |
| Intrinsic frame / rigid motion | Y (migration) | Y | Y | P1 analysis APIs |

## Knot catalog JS (Node)

VortexLab-compatible catalogs: `resources/knots_data_{ideal,fourier,knotplot}.js` via `resources/load_knot_catalogs.js`.  
C++ `KnotCatalog` adds native sampling/metadata for the same sources where embedded.

## Policy

Do not copy VortexLab algorithms into TypeScript/JavaScript when the numeric path belongs in `sstcore_lib`. Prefer N-API binds that call the same functions Python already uses.
