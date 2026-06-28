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

- single objects: **160**
- single attachment result rows: **1920**
- multicomponent links parsed: **24**
- link attachment result rows: **288**
- gear mesh rows: **0**
- gear lock scenarios: **0**

## Single-object classes

Class counts: `{'single_twist': 25, 'single_general': 124, 'single_torus': 11}`

| object | type | base rule | base | status |
|---|---|---|---:|---|
| `fremlin_fseries:10_1/knot.10_1.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:10_1/knot.10_1n.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:12a_1202/knot.12a_1202.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:12a_1202/knot.12a_1202z6.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:15331/knot.15331.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:1_1/knot.1_1.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:3_1/knot.3_1.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 6 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:3_1/knot.3_1p.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 6 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:3_1/knot.3_1u.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 6 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:4_1/knot.4_1.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:4_1/knot.4_1d.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:4_1/knot.4_1p.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:4_1/knot.4_1z.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:5_1/knot.5_1.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 10 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:5_1/knot.5_1p.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 10 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:5_1/knot.5_1u.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 10 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:5_2/knot.5_2.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:5_2/knot.5_2d.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:5_2/knot.5_2r.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_1/knot.6_1.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_2/knot.6_2.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_2/knot.6_2d.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_2/knot.6_2p.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_3/knot.6_3d.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:6_3/knot.6_3z.fseries` | `single_general` | `general_attachment_only_no_geom_SL` | 0 | `DIAGNOSTIC_GENERAL_ATTACHMENT_ONLY` |
| `fremlin_fseries:7_1/knot.7_1.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 14 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:7_1/knot.7_1p.fseries` | `single_torus` | `torus_pq_by_label_batch_unverified` | 14 | `SOURCE_CLASSIFIED_TORUS_PQ_UNVERIFIED` |
| `fremlin_fseries:7_2/knot.7_2.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:7_2/knot.7_2d.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| `fremlin_fseries:7_2/knot.7_2r.fseries` | `single_twist` | `twist_attachment_only_no_pq_rule` | 0 | `DIAGNOSTIC_TWIST_ATTACHMENT_ONLY` |
| ... | ... | ... | ... | 130 more rows in CSV |

## Single attachment audit status counts

`{'BASELINE_EXACT_ATTACHMENT': 640, 'CANON_CANDIDATE_EXACT_COMPENSATED': 1280}`

## Link objects

| object | components | source | member |
|---|---:|---|---|
| `ideal:0:1:2` | 2 | `ideal.txt` | `0:1:2` |
| `knot_0.2.1` | 2 | `knotplot\knot_0.2.1\knot_0.2.1.txt` | `knot_0.2.1.txt` |
| `knot_0.3.1` | 3 | `knotplot\knot_0.3.1\knot_0.3.1.txt` | `knot_0.3.1.txt` |
| `knot_2.2.1` | 2 | `knotplot\knot_2.2.1\knot_2.2.1.txt` | `knot_2.2.1.txt` |
| `knot_4.2.1` | 2 | `knotplot\knot_4.2.1\knot_4.2.1.txt` | `knot_4.2.1.txt` |
| `knot_5.2.1` | 2 | `knotplot\knot_5.2.1\knot_5.2.1.txt` | `knot_5.2.1.txt` |
| `knot_6.2.1` | 2 | `knotplot\knot_6.2.1\knot_6.2.1.txt` | `knot_6.2.1.txt` |
| `knot_6.3.1` | 3 | `knotplot\knot_6.3.1\knot_6.3.1.txt` | `knot_6.3.1.txt` |
| `knot_6.3.2` | 3 | `knotplot\knot_6.3.2\knot_6.3.2.txt` | `knot_6.3.2.txt` |
| `knot_6.3.3` | 3 | `knotplot\knot_6.3.3\knot_6.3.3.txt` | `knot_6.3.3.txt` |
| `knot_7.2.5` | 2 | `knotplot\knot_7.2.5\knot_7.2.5.txt` | `knot_7.2.5.txt` |
| `knot_7.2.6` | 2 | `knotplot\knot_7.2.6\knot_7.2.6.txt` | `knot_7.2.6.txt` |
| `knot_7.2.8` | 2 | `knotplot\knot_7.2.8\knot_7.2.8.txt` | `knot_7.2.8.txt` |
| `knot_8.2.1` | 2 | `knotplot\knot_8.2.1\knot_8.2.1.txt` | `knot_8.2.1.txt` |
| `knot_9.2.20` | 2 | `knotplot\knot_9.2.20\knot_9.2.20.txt` | `knot_9.2.20.txt` |
| `knot_9.2.40` | 2 | `knotplot\knot_9.2.40\knot_9.2.40.txt` | `knot_9.2.40.txt` |
| `knot_TL2.4` | 2 | `knotplot\knot_TL2.4\knot_TL2.4.txt` | `knot_TL2.4.txt` |
| `knot_TL2.6` | 2 | `knotplot\knot_TL2.6\knot_TL2.6.txt` | `knot_TL2.6.txt` |
| `knot_TL2.8` | 2 | `knotplot\knot_TL2.8\knot_TL2.8.txt` | `knot_TL2.8.txt` |
| `knot_TL3.3_Gear` | 3 | `knotplot\knot_TL3.3_Gear\knot_TL3.3_Gear.txt` | `knot_TL3.3_Gear.txt` |
| `knot_TL3.6` | 3 | `knotplot\knot_TL3.6\knot_TL3.6.txt` | `knot_TL3.6.txt` |
| `knot_TL3.9` | 3 | `knotplot\knot_TL3.9\knot_TL3.9.txt` | `knot_TL3.9.txt` |
| `knot_TL6.15` | 3 | `knotplot\knot_TL6.15\knot_TL6.15.txt` | `knot_TL6.15.txt` |
| `knot_TL6.9` | 3 | `knotplot\knot_TL6.9\knot_TL6.9.txt` | `knot_TL6.9.txt` |

## Link attachment audit status counts

`{'LINK_CANON_CANDIDATE_EXACT_COMPENSATED': 288}`

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
