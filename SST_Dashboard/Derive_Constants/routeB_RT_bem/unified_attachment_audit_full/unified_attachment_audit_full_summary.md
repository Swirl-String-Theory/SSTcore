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

- single objects: **34**
- single attachment result rows: **1224**
- multicomponent links parsed: **0**
- link attachment result rows: **0**
- gear mesh rows: **2**
- gear lock scenarios: **8**

## Single-object classes

Class counts: `{'single_torus': 27, 'single_twist': 7}`

| object | type | base rule | base | status |
|---|---|---|---:|---|
| `analytic:T(2,3)` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `analytic:T(2,5)` | `single_torus` | `torus_surface_pq` | 10 | `CANONICAL_TORUS_BASE` |
| `analytic:T(2,7)` | `single_torus` | `torus_surface_pq` | 14 | `CANONICAL_TORUS_BASE` |
| `analytic:T(2,9)` | `single_torus` | `torus_surface_pq` | 18 | `CANONICAL_TORUS_BASE` |
| `analytic:T(2,11)` | `single_torus` | `torus_surface_pq` | 22 | `CANONICAL_TORUS_BASE` |
| `analytic:T(3,2)` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `analytic:T(3,4)` | `single_torus` | `torus_surface_pq` | 12 | `CANONICAL_TORUS_BASE` |
| `ideal:3:1:1` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `ideal:5:1:1` | `single_torus` | `fitted_torus_proxy_noncanonical` | 9 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `ideal:5:1:2 (5_2_twist_control)` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 5 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `ideal:7:1:1` | `single_torus` | `fitted_torus_proxy_noncanonical` | 13 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `ideal:9:1:1` | `single_torus` | `fitted_torus_proxy_noncanonical` | 15 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `ideal:K11a367` | `single_torus` | `fitted_torus_proxy_noncanonical` | 19 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `ideal:K11a247 (11_2_twist_control)` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 8 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | `single_torus` | `fitted_torus_proxy_noncanonical` | 1 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `single_torus` | `torus_surface_pq` | 10 | `CANONICAL_TORUS_BASE` |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | `single_torus` | `fitted_torus_proxy_noncanonical` | 3 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `single_torus` | `torus_surface_pq` | 10 | `CANONICAL_TORUS_BASE` |
| `Knots_FourierSeries/5_2/knot.5_2.fseries` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 5 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `Knots_FourierSeries/5_2/knot.5_2d.fseries` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `Knots_FourierSeries/5_2/knot.5_2r.fseries` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `single_torus` | `torus_surface_pq` | 14 | `CANONICAL_TORUS_BASE` |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | `single_torus` | `fitted_torus_proxy_noncanonical` | 12 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `single_torus` | `torus_surface_pq` | 6 | `CANONICAL_TORUS_BASE` |
| `knotplot/knot_5.1/knot_5.1.fseries` | `single_torus` | `fitted_torus_proxy_noncanonical` | 9 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| `knotplot/knot_5.2/knot_5.2.fseries` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 5 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `knotplot/knot_5.2.1/knot_5.2.1.fseries` | `single_twist` | `PT_Lk0_round_proxy_no_pq_rule` | 1 | `DIAGNOSTIC_TWIST_OR_GENERAL_PROXY` |
| `knotplot/knot_7.1/knot_7.1.fseries` | `single_torus` | `fitted_torus_proxy_noncanonical` | 11 | `DIAGNOSTIC_NONCANONICAL_TORUS_FIT` |
| ... | ... | ... | ... | 4 more rows in CSV |

## Single attachment audit status counts

`{'BASELINE_EXACT_ATTACHMENT': 136, 'CANON_CANDIDATE_EXACT_COMPENSATED': 408, 'LOCAL_ONLY_TRIVIAL_EPS0': 34, 'FAILS_ATTACHMENT_AUDIT': 68, 'DECOHERED_SELECTION_STABLE_NOT_EXACT': 136, 'PASSIVE_TRANSIT_REJECTED': 136, 'SELECTION_STABLE_BUT_HOLONOMY_NOT_EXACT': 102, 'PARTIAL_SELECTION_STABLE_NOT_EXACT': 102, 'CHARGE_LEAK_REJECT_OR_CONSTRAIN': 102}`

## Gear/STL module

| mesh | bodies | extents | watertight |
|---|---:|---|---|
| `gear_stl` | 3 | 69.9119968414 x 74.1188621521 x 45.4024124146 | `YES` |
| `axle_stl` | 1 | 13.2388634682 x 13.239464283 x 300.666748047 | `YES` |

## Gear lock scenario counts

`{'FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION': 4, 'FULLY_LOCKED_ATTACHMENT_ANALOG': 4}`

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
```

## Audit warning

This script is an audit harness and model classifier, not a proof machine. Exact neutral compensation remains the physical load-bearing gate.
