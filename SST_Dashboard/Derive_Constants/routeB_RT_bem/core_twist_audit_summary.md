# Core-twist audit summary

Generated: 2026-06-25 19:33:38

## Scope

This audit separates three statements that must not be conflated:

```text
[DERIVED CHECK]    torus-surface framing: |SL_torus(T(p,q))| = p q
[POSITED CHECK]    physical SST core adds n_core = +1
[CONDITIONAL]      |SL_phys| = p q + 1 iff n_core = +1
[CIRCULARITY TRAP] arbitrary target injection can PASS any integer target
```

Curves analysed: **34**; energy landscape rows: **189**
Samples: **1024**; q-list: `3,5,7,9,11`; n-core range: `-3:3`

## A. Target-free analytic torus-surface framing

These rows are the non-circular check. No `2q+1` target is injected; the offset direction is the analytic torus surface normal.

| curve | expected pq | measured SL | |SL|-pq err | status | n needed for pq+1 |
|---|---:|---:|---:|---|---:|
| `analytic:T(2,3)` | 6 | -6.00048 | 0.000483428 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,5)` | 10 | -10.0014 | 0.00137761 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,7)` | 14 | -14.0041 | 0.00412962 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,9)` | 18 | -18.0124 | 0.0123509 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,11)` | 22 | -22.0324 | 0.032441 | PASS_DERIVED_PQ | 1 |
| `analytic:T(3,2)` | 6 | -6.00287 | 0.00286766 | PASS_DERIVED_PQ | 1 |
| `analytic:T(3,4)` | 12 | -12.0057 | 0.0056946 | PASS_DERIVED_PQ | 1 |

## B. Source curves: fitted torus-framing diagnostic

For ideal/fseries curves the fitted torus normal is diagnostic only. A mismatch means the source conformation/framing is not the canonical torus-surface embedding; it does not falsify the analytic theorem.

| source | expected pq | fitted SL | abs err | PT Lk0 | status |
|---|---:|---:|---:|---:|---|
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 6 | 6.00045 | 0.000447049 | 2.99998 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 6 | 0.584235 | 5.41577 | 4.0002 | SOURCE_FIT_NOT_CANONICAL |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 6 | 6.002 | 0.00199934 | 4.00035 | PASS_DERIVED_PQ |
| `ideal:3:1:1` | 6 | -6.00021 | 0.000214432 | -2.99988 | PASS_DERIVED_PQ |
| `knotplot/knot_3.1/knot_3.1.fseries` | 6 | 6.00028 | 0.000280875 | 3.00006 | PASS_DERIVED_PQ |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | 6 | -6.00027 | 0.00026855 | -3.00006 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 10 | 10.0037 | 0.00371321 | 7.00021 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 10 | 3.56347 | 6.43653 | 6.00033 | SOURCE_FIT_NOT_CANONICAL |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 10 | 10.0291 | 0.0291084 | 8.00576 | PASS_DERIVED_PQ |
| `ideal:5:1:1` | 10 | -9.00049 | 0.999506 | -5.99972 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_5.1/knot_5.1.fseries` | 10 | 9.0002 | 0.999796 | 6.00018 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 10 | -10.001 | 0.000997047 | -6.00014 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 14 | 14.0042 | 0.00417327 | 9.00015 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 14 | 12.6868 | 1.31321 | 9.00111 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:7:1:1` | 14 | 13.0048 | 0.995164 | 8.99972 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_7.1/knot_7.1.fseries` | 14 | 11.0007 | 2.99934 | 9.00047 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | 14 | -10.9998 | 3.00017 | -9.00037 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:9:1:1` | 18 | 15.0014 | 2.99862 | 11.9996 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_9.1/knot_9.1.fseries` | 18 | 15.0018 | 2.99816 | 12.001 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:K11a367` | 22 | -19.0084 | 2.99164 | -14.9997 | SOURCE_FIT_NOT_CANONICAL |

## C. Core-twist audit

For every row with a target-free torus framing, the lepton-ladder value `pq+1` requires exactly:

```text
n_core_required = (pq + 1) - |round(SL_torus)|
```

If `n_core_required = 1`, the old `pq+1` rule has been reduced to the single open rule `n_core=+1`.

| source | pq | |SL(n=0)| | |SL(n=+1)| | required n | selected by null | selected by model | model status |
|---|---:|---:|---:|---:|---:|---:|---|
| `analytic:T(3,2)` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(2,3)` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(3,4)` | 12 | 12 | 13 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(2,5)` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(2,7)` | 14 | 14 | 15 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(2,9)` | 18 | 18 | 19 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `analytic:T(2,11)` | 22 | 22 | 23 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 6 | 1 | 2 | 6 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_3.1/knot_3.1.fseries` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 10 | 4 | 5 | 7 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_5.1/knot_5.1.fseries` | 10 | 9 | 10 | 2 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 14 | 14 | 15 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 14 | 13 | 14 | 2 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_7.1/knot_7.1.fseries` | 14 | 11 | 12 | 4 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | 14 | 11 | 12 | 4 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_9.1/knot_9.1.fseries` | 18 | 15 | 16 | 4 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `ideal:3:1:1` | 6 | 6 | 7 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `ideal:5:1:1` | 10 | 9 | 10 | 2 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `ideal:7:1:1` | 14 | 13 | 14 | 2 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `ideal:9:1:1` | 18 | 15 | 16 | 4 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `ideal:K11a367` | 22 | 19 | 20 | 4 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |

Energy note: `E_model` uses `core_n0` as an explicit model input. With the default `core_n0=1`, the script reports `MODEL_INPUT_SELECTS_PLUS_ONE`, not `[DERIVED]`.

## D. Twist / non-torus controls

These are intentionally not tested against the torus pq or pq+1 rule.

| control | for q | Wr | PT Lk0 | status | notes |
|---|---:|---:|---:|---|---|
| `Knots_FourierSeries/5_2/knot.5_2.fseries` | 5 | 4.81395 | 5.00077 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `Knots_FourierSeries/5_2/knot.5_2d.fseries` | 5 | 1.13404e-11 | -4.06263e-13 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `Knots_FourierSeries/5_2/knot.5_2r.fseries` | 5 | 3.29752 | 1.9893 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `ideal:5:1:2 (5_2_twist_control)` | 5 | 4.54669 | 5.00082 | control_twist | Brian Gilbert ideal id 5:1:2 / user-labelled 5_2 twist control; torus pq rule not applied |
| `ideal:K11a247 (11_2_twist_control)` | 11 | 7.93943 | 8.00575 | control_twist | Knot Atlas K11a247 / user-labelled 11_2 twist control; torus pq rule not applied |
| `knotplot/knot_5.2.1/knot_5.2.1.fseries` | 5 | 0.539559 | 1.00143 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `knotplot/knot_5.2/knot_5.2.fseries` | 5 | 4.61056 | 5.00051 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |

## E. Circularity trap

Trap target: `25`. Status counts: `{'PASS_ANY_TARGET': 23, 'CHECK_TRAP': 4}`

If these pass, that proves integer target-injection is circular: the same method can manufacture an arbitrary self-linking target.

| source | trap target | trap Lk | err | status |
|---|---:|---:|---:|---|
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 25 | 25.035 | 0.0350306 | PASS_ANY_TARGET |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 25 | 25.0348 | 0.0347688 | PASS_ANY_TARGET |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 25 | 25.0535 | 0.0535371 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 25 | 25.0374 | 0.0373837 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 25 | 25.0352 | 0.0351924 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 25 | 25.3262 | 0.326191 | CHECK_TRAP |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 25 | 25.0244 | 0.0244457 | PASS_ANY_TARGET |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 25 | 25.0336 | 0.0335795 | PASS_ANY_TARGET |
| `analytic:T(2,11)` | 25 | 25.4511 | 0.451144 | CHECK_TRAP |
| `analytic:T(2,3)` | 25 | 25.0741 | 0.0741167 | PASS_ANY_TARGET |
| `analytic:T(2,5)` | 25 | 25.1038 | 0.10377 | PASS_ANY_TARGET |
| `analytic:T(2,7)` | 25 | 25.1564 | 0.1564 | PASS_ANY_TARGET |
| `analytic:T(2,9)` | 25 | 25.2559 | 0.255906 | CHECK_TRAP |
| `analytic:T(3,2)` | 25 | 25.1208 | 0.120825 | PASS_ANY_TARGET |
| `analytic:T(3,4)` | 25 | 25.1637 | 0.163695 | PASS_ANY_TARGET |
| `ideal:3:1:1` | 25 | 25.0745 | 0.0745133 | PASS_ANY_TARGET |
| `ideal:5:1:1` | 25 | 25.105 | 0.105048 | PASS_ANY_TARGET |
| `ideal:7:1:1` | 25 | 25.0192 | 0.0192254 | PASS_ANY_TARGET |
| `ideal:9:1:1` | 25 | 25.0215 | 0.0215363 | PASS_ANY_TARGET |
| `ideal:K11a367` | 25 | 25.3158 | 0.315825 | CHECK_TRAP |
| `knotplot/knot_3.1/knot_3.1.fseries` | 25 | 25.0334 | 0.0333628 | PASS_ANY_TARGET |
| `knotplot/knot_5.1/knot_5.1.fseries` | 25 | 25.0242 | 0.0241585 | PASS_ANY_TARGET |
| `knotplot/knot_7.1/knot_7.1.fseries` | 25 | 25.0189 | 0.0189099 | PASS_ANY_TARGET |
| `knotplot/knot_9.1/knot_9.1.fseries` | 25 | 25.0194 | 0.0194494 | PASS_ANY_TARGET |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | 25 | 25.074 | 0.0739569 | PASS_ANY_TARGET |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 25 | 25.1011 | 0.101057 | PASS_ANY_TARGET |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | 25 | 25.1346 | 0.134626 | PASS_ANY_TARGET |

## Audit labels

```text
[DERIVED]      |SL_torus(T(p,q))| = p q for target-free torus-surface framing, if analytic rows pass.
[POSITED]      n_core = +1 unless an independent background/core model derives core_n0=1.
[CONDITIONAL]  |SL_phys| = p q + 1 iff n_core=+1.
[CIRCULAR]     Any test that sets extra_k = target - round(Lk0) and then confirms target.
[CONTROL]      5_2 / 11_2 twist knots are non-torus controls, not falsifiers of the T(2,q) rule.
```
