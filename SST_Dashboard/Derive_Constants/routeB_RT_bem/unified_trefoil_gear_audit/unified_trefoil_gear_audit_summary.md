# Unified Compensated Attachment Audit Summary

## Purpose

This audit tests compensated swirl-clock / entanglement attachment across single torus knots, twist/general single-component controls, multicomponent links, and optional gear-locked STL analogs.

```text
chi_total = chi_local + chi_attachment
Canon-safe mode: chi_total = chi, charge_leak = 0, FR odd parity active
Important distinction: integer selection may survive approximate holonomy, but exact Canon requires exact holonomy.
```

## Canonical constants

| quantity | value |
|---|---:|
| `||v_swirl||` | 1.093845630000e+06 m/s |
| `r_c` | 1.408970170000e-15 m |
| `Omega_core` | 7.763440655383e+20 s^-1 |
| `T_core` | 8.093299847437e-21 s |
| `Omega_core*T_core/(2π)` | 1.000000000000 turns |
| `omega_vorticity*T_core/(2π)` | 2.000000000000 vorticity-turns |

## Inputs and row counts

- single objects: **0**
- single attachment result rows: **0**
- multicomponent links parsed: **0**
- link attachment result rows: **0**
- gear mesh rows: **0**
- gear lock scenarios: **0**
- trefoil-gear mesh rows: **6**
- trefoil-gear analog rows: **1**

## Segmented trefoil gear/STL module

| object | segments | blade turns | per segment | profile symmetry | status |
|---|---:|---:|---:|---:|---|
| `segmented_trefoil_gear_variant` | 3 | 10.0 | 3.3333333333333335 | 3 | `SEGMENTED_TREFOIL_FRAMED_TUBE_ATTACHMENT_ANALOG_WITH_CORE_SPINE` |

Interpretation: blade/shell turns are treated as a mechanical gearing budget, not as direct `n_core`. The core Attachment target remains `chi=1` in the matter sector.

## Canon-candidate statement

```text
[CONDITIONAL CANON-CANDIDATE]
If a compensated neutral core/framing connection exists such that
Hol(A_core)/(2π) = chi_local + chi_attachment = chi,
with charge_leak = 0 and FR odd parity active, then positive twist stiffness selects
n_core = chi.

For torus knots:        SL_phys(T(p,q)) = pq + chi.
For twist/general knots: SL_phys(K) = SL_geom_proxy(K) + chi, with proxy status explicit.
For multicomponent links: H/Gamma^2 = sum_i(SL_i + chi_i) + 2 sum_ij Lk_ij + higher.
For gear STL analogs: fully locked sign sectors support a mechanical global-attachment analog.
For segmented trefoil STL analogs: keyed 3-blade framed-tube segments support a single-component core-spine attachment analog.
```

## Audit warning

This script is an audit harness and model classifier, not a proof machine. Exact neutral compensation remains the physical load-bearing gate.
