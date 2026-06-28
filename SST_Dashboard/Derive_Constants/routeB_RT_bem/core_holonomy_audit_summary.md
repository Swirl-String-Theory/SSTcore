# Core-holonomy audit summary

Generated: 2026-06-25 15:35:21

## Question

```text
n_core = (1/2π) ∮_K dθ_core  ?=  1
SL_phys(T(p,q)) = SL_torus + n_core
```

The non-circular theorem checked upstream is `|SL_torus(T(p,q))| = p q`. This audit asks which physical/core-holonomy model selects the missing `+1` without injecting `pq+1` as a target.

Curves/models analysed: **204** result rows; energy rows: **1134**.
Models: `zero,unit,canon_core_cycle,twoomega_cycle,twoomega_transit,background`; n range: `-3:3`; samples: **1024**.

## A. Clean analytic theorem rows

| curve | pq | SL_torus | required n_core |
|---|---:|---:|---:|
| `analytic:T(2,3)` | 6 | -6.00048 | 1 |
| `analytic:T(2,5)` | 10 | -10.0014 | 1 |
| `analytic:T(2,7)` | 14 | -14.0041 | 1 |
| `analytic:T(2,9)` | 18 | -18.0124 | 1 |
| `analytic:T(2,11)` | 22 | -22.0324 | 1 |
| `analytic:T(3,2)` | 6 | -6.00287 | 1 |
| `analytic:T(3,4)` | 12 | -12.0057 | 1 |

## B. Model selection overview

| model | rows | selects required | rejects required | typical status |
|---|---:|---:|---:|---|
| `background` | 27 | 16 | 11 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST; SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `canon_core_cycle` | 27 | 16 | 11 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST; SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `twoomega_cycle` | 27 | 16 | 11 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST; SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `twoomega_transit` | 27 | 1 | 26 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST; SELECTS_REQUIRED_IN_TRANSIT_MODEL` |
| `unit` | 27 | 16 | 11 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST; SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `zero` | 27 | 0 | 27 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |

## C. Clean rows where required +1 is selected

| curve | model | Φ/(2π) | selected n | epistemic status |
|---|---|---:|---:|---|
| `analytic:T(2,3)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,3)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(2,3)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(2,3)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,5)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,5)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(2,5)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(2,5)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,7)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,7)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(2,7)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(2,7)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,9)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,9)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(2,9)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(2,9)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,11)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(2,11)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(2,11)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(2,11)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(3,2)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(3,2)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(3,2)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(3,2)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(3,4)` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `analytic:T(3,4)` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `analytic:T(3,4)` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `analytic:T(3,4)` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `ideal:3:1:1` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `ideal:3:1:1` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `ideal:3:1:1` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `ideal:3:1:1` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `unit` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `canon_core_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CANON_CORE_CYCLE` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `twoomega_cycle` | 1 | 1 | `SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `background` | 1 | 1 | `SELECTS_REQUIRED_BY_INPUT_ASSUMPTION` |

## D. Clean rows rejecting +1

| curve | model | Φ/(2π) | selected n | required n | status |
|---|---|---:|---:|---:|---|
| `analytic:T(2,3)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,3)` | `twoomega_transit` | 2.12514 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,5)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,5)` | `twoomega_transit` | 2.46657 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,7)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,7)` | `twoomega_transit` | 2.89954 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,9)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,9)` | `twoomega_transit` | 3.38894 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,11)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(2,11)` | `twoomega_transit` | 3.91391 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(3,2)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(3,2)` | `twoomega_transit` | 2.92282 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(3,4)` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `analytic:T(3,4)` | `twoomega_transit` | 3.12094 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `ideal:3:1:1` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `ideal:3:1:1` | `twoomega_transit` | 2.10402 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | `twoomega_transit` | 2.22161 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | `twoomega_transit` | 2.82358 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | `twoomega_transit` | 2.78575 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | `twoomega_transit` | 4.53825 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | `twoomega_transit` | 2.74632 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_3.1/knot_3.1.fseries` | `twoomega_transit` | 2.09472 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | `twoomega_transit` | 2.10786 | 2 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `zero` | 0 | 0 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | `twoomega_transit` | 2.50179 | 3 | 1 | `DOES_NOT_SELECT_REQUIRED_CORE_TWIST` |

## E. Interpretation labels

```text
[DERIVED]       |SL_torus(T(p,q))| = p q, from target-free torus-surface framing.
[ISOLATED]      pq+1 reduces to n_core = 1 for clean torus rows.
[INPUT]         unit/signed_unit/background models select +1 only because Φ_bg/(2π)=1 is supplied.
[CANON-CYCLE]   canon_core_cycle selects +1 from Ω_core=v_swirl/r_c and T_core=2πr_c/v_swirl; still a closure model, but uses canonical constants rather than pq+1.
[CLOSURE]       twoomega_cycle selects +1 if Ω_core T_cycle = 2π is accepted as a closure condition.
[DIAGNOSTIC]    twoomega_transit tests a material transit model; it need not be q-independent.
[OPEN]          justify why the canonical local core cycle is the physical holonomy attached to every closed swirl string, rather than a mere local period identity.
```
