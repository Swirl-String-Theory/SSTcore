# Core-twist audit summary

Generated: 2026-06-25 19:35:49

## Scope

This audit separates three statements that must not be conflated:

```text
[DERIVED CHECK]    torus-surface framing: |SL_torus(T(p,q))| = p q
[POSITED CHECK]    physical SST core adds n_core = +1
[CONDITIONAL]      |SL_phys| = p q + 1 iff n_core = +1
[CIRCULARITY TRAP] arbitrary target injection can PASS any integer target
```

Curves analysed: **34**; energy landscape rows: **189**
Samples: **2048**; q-list: `3,5,7,9,11`; n-core range: `-3:3`

## A. Target-free analytic torus-surface framing

These rows are the non-circular check. No `2q+1` target is injected; the offset direction is the analytic torus surface normal.

| curve | expected pq | measured SL | |SL|-pq err | status | n needed for pq+1 |
|---|---:|---:|---:|---|---:|
| `analytic:T(2,3)` | 6 | -6.00007 | 7.32939e-05 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,5)` | 10 | -10.0002 | 0.000167504 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,7)` | 14 | -14.0003 | 0.000337442 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,9)` | 18 | -18.0007 | 0.000662618 | PASS_DERIVED_PQ | 1 |
| `analytic:T(2,11)` | 22 | -22.0012 | 0.00124573 | PASS_DERIVED_PQ | 1 |
| `analytic:T(3,2)` | 6 | -6.00012 | 0.000115503 | PASS_DERIVED_PQ | 1 |
| `analytic:T(3,4)` | 12 | -12.0003 | 0.000317041 | PASS_DERIVED_PQ | 1 |

## B. Source curves: fitted torus-framing diagnostic

For ideal/fseries curves the fitted torus normal is diagnostic only. A mismatch means the source conformation/framing is not the canonical torus-surface embedding; it does not falsify the analytic theorem.

| source | expected pq | fitted SL | abs err | PT Lk0 | status |
|---|---:|---:|---:|---:|---|
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 6 | 6.00006 | 5.79198e-05 | 3.00001 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 6 | 0.82659 | 5.17341 | 4.00004 | SOURCE_FIT_NOT_CANONICAL |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 6 | 6.0001 | 9.88071e-05 | 4.00006 | PASS_DERIVED_PQ |
| `ideal:3:1:1` | 6 | -6.00004 | 4.13205e-05 | -2.99997 | PASS_DERIVED_PQ |
| `knotplot/knot_3.1/knot_3.1.fseries` | 6 | 6.00007 | 6.57929e-05 | 3.00001 | PASS_DERIVED_PQ |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | 6 | -6.00007 | 6.53442e-05 | -3.00002 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 10 | 10.0001 | 0.000128646 | 6.99999 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 10 | 3.13367 | 6.86633 | 6.00014 | SOURCE_FIT_NOT_CANONICAL |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 10 | 10.0007 | 0.000684699 | 8.00036 | PASS_DERIVED_PQ |
| `ideal:5:1:1` | 10 | -9.00004 | 0.999963 | -5.99994 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_5.1/knot_5.1.fseries` | 10 | 9.00004 | 0.999961 | 6.00005 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 10 | -10.0002 | 0.000233728 | -6.00004 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 14 | 14.0004 | 0.000370745 | 9.00004 | PASS_DERIVED_PQ |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 14 | 11.5077 | 2.49228 | 9.00036 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:7:1:1` | 14 | 13.0011 | 0.99888 | 8.99994 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_7.1/knot_7.1.fseries` | 14 | 11.0002 | 2.9998 | 9.00011 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | 14 | -11 | 2.99999 | -9.00009 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:9:1:1` | 18 | 15.0002 | 2.99979 | 11.9999 | SOURCE_FIT_NOT_CANONICAL |
| `knotplot/knot_9.1/knot_9.1.fseries` | 18 | 15.0004 | 2.99963 | 12.0002 | SOURCE_FIT_NOT_CANONICAL |
| `ideal:K11a367` | 22 | -19.0006 | 2.99945 | -14.9999 | SOURCE_FIT_NOT_CANONICAL |

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
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 10 | 3 | 4 | 8 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_5.1/knot_5.1.fseries` | 10 | 9 | 10 | 2 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 10 | 10 | 11 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 14 | 14 | 15 | 1 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 14 | 12 | 13 | 3 | 0 | 1 | MODEL_INPUT_SELECTS_PLUS_ONE |
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
| `Knots_FourierSeries/5_2/knot.5_2.fseries` | 5 | 4.81338 | 5.00018 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `Knots_FourierSeries/5_2/knot.5_2d.fseries` | 5 | 9.72543e-14 | 1.23688e-13 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `Knots_FourierSeries/5_2/knot.5_2r.fseries` | 5 | 3.3109 | 0.316815 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `ideal:5:1:2 (5_2_twist_control)` | 5 | 4.54594 | 5.00018 | control_twist | Brian Gilbert ideal id 5:1:2 / user-labelled 5_2 twist control; torus pq rule not applied |
| `ideal:K11a247 (11_2_twist_control)` | 11 | 7.93375 | 8.00141 | control_twist | Knot Atlas K11a247 / user-labelled 11_2 twist control; torus pq rule not applied |
| `knotplot/knot_5.2.1/knot_5.2.1.fseries` | 5 | 0.536995 | 1.00034 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |
| `knotplot/knot_5.2/knot_5.2.fseries` | 5 | 4.61014 | 5.00012 | control_twist | fseries label matched 5_2 twist control; torus pq rule not applied |

## E. Circularity trap

Trap target: `25`. Status counts: `{'PASS_ANY_TARGET': 27}`

If these pass, that proves integer target-injection is circular: the same method can manufacture an arbitrary self-linking target.

| source | trap target | trap Lk | err | status |
|---|---:|---:|---:|---|
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 25 | 25.0082 | 0.0082142 | PASS_ANY_TARGET |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 25 | 25.0081 | 0.00806482 | PASS_ANY_TARGET |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 25 | 25.0078 | 0.0078239 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 25 | 25.0056 | 0.00564222 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 25 | 25.0061 | 0.00613983 | PASS_ANY_TARGET |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 25 | 25.008 | 0.00796972 | PASS_ANY_TARGET |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 25 | 25.0042 | 0.00420408 | PASS_ANY_TARGET |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 25 | 25.005 | 0.00495565 | PASS_ANY_TARGET |
| `analytic:T(2,11)` | 25 | 25.0648 | 0.0647767 | PASS_ANY_TARGET |
| `analytic:T(2,3)` | 25 | 25.0179 | 0.0179324 | PASS_ANY_TARGET |
| `analytic:T(2,5)` | 25 | 25.0244 | 0.0244364 | PASS_ANY_TARGET |
| `analytic:T(2,7)` | 25 | 25.0341 | 0.0341289 | PASS_ANY_TARGET |
| `analytic:T(2,9)` | 25 | 25.0474 | 0.0474218 | PASS_ANY_TARGET |
| `analytic:T(3,2)` | 25 | 25.0195 | 0.0195041 | PASS_ANY_TARGET |
| `analytic:T(3,4)` | 25 | 25.0293 | 0.0293196 | PASS_ANY_TARGET |
| `ideal:3:1:1` | 25 | 25.0185 | 0.0184746 | PASS_ANY_TARGET |
| `ideal:5:1:1` | 25 | 25.0251 | 0.0251145 | PASS_ANY_TARGET |
| `ideal:7:1:1` | 25 | 25.0039 | 0.00392872 | PASS_ANY_TARGET |
| `ideal:9:1:1` | 25 | 25.0027 | 0.00269425 | PASS_ANY_TARGET |
| `ideal:K11a367` | 25 | 25.0549 | 0.0548979 | PASS_ANY_TARGET |
| `knotplot/knot_3.1/knot_3.1.fseries` | 25 | 25.0082 | 0.00824457 | PASS_ANY_TARGET |
| `knotplot/knot_5.1/knot_5.1.fseries` | 25 | 25.0058 | 0.0058102 | PASS_ANY_TARGET |
| `knotplot/knot_7.1/knot_7.1.fseries` | 25 | 25.0041 | 0.00410163 | PASS_ANY_TARGET |
| `knotplot/knot_9.1/knot_9.1.fseries` | 25 | 25.0029 | 0.00290115 | PASS_ANY_TARGET |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | 25 | 25.0183 | 0.0183489 | PASS_ANY_TARGET |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | 25 | 25.0246 | 0.0246444 | PASS_ANY_TARGET |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | 25 | 25.0322 | 0.032211 | PASS_ANY_TARGET |

## Audit labels

```text
[DERIVED]      |SL_torus(T(p,q))| = p q for target-free torus-surface framing, if analytic rows pass.
[POSITED]      n_core = +1 unless an independent background/core model derives core_n0=1.
[CONDITIONAL]  |SL_phys| = p q + 1 iff n_core=+1.
[CIRCULAR]     Any test that sets extra_k = target - round(Lk0) and then confirms target.
[CONTROL]      5_2 / 11_2 twist knots are non-torus controls, not falsifiers of the T(2,q) rule.
```
