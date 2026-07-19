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

## Needs wrapper only (C++ already in `sstcore_lib`)

- Exact / continuous Fourier curvature  
- Gauss writhe variant  
- Resolved-tube DCSD, `reach_rad`, segment–segment multi-component gaps  

## Needs new C++ (or stays in VortexLab JS)

- Named **topology clearance** guard as used in VortexLab HTML  

## Policy

Do not copy VortexLab algorithms into TypeScript/JavaScript when the numeric path belongs in `sstcore_lib`. Prefer N-API binds that call the same functions Python already uses.
