# Framed-helicity test summary

Generated: 2026-06-25 03:50:00

Core diagnostic:

```text
H/Gamma^2 = SL = Wr + Tw
SL_target(T(2,q)) = 2q + 1
Tw_target = SL_target - Wr
```

Total curves analysed: **27**
Targeted torus-ladder curves: **20**
Samples per curve: **1024**

## T(2,3) target SL = 7

| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `knotplot/knot_3.1/knot_3.1.fseries` | 3.37927 | 3.00007 | 4 | 3.62073 | 7.00042 | 0.000422134 | PASS |
| `Knots_FourierSeries/3_1/knot.3_1.fseries` | 3.41836 | 3.00004 | 4 | 3.58164 | 7.00042 | 0.000422354 | PASS |
| `Knots_FourierSeries/3_1/knot.3_1p.fseries` | 3.59542 | 4.00017 | 3 | 3.40458 | 7.00048 | 0.000477455 | PASS |
| `Knots_FourierSeries/3_1/knot.3_1u.fseries` | 3.89271 | 4.00024 | 3 | 3.10729 | 7.00062 | 0.000622816 | PASS |
| `knotplot/knot_T2.3/knot_T2.3.fseries` | -3.39506 | -3.00007 | 10 | 10.3951 | 7.00399 | 0.00398631 | PASS |
| `ideal:3:1:1` | -3.418 | -2.99993 | 10 | 10.418 | 7.00423 | 0.0042291 | PASS |

## T(2,5) target SL = 11

| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `knotplot/knot_5.1/knot_5.1.fseries` | 6.13773 | 6.00022 | 5 | 4.86227 | 11.0011 | 0.00111016 | PASS |
| `Knots_FourierSeries/5_1/knot.5_1.fseries` | 6.69007 | 7.00008 | 4 | 4.30993 | 11.0011 | 0.00112436 | PASS |
| `Knots_FourierSeries/5_1/knot.5_1p.fseries` | 6.41878 | 6.00061 | 5 | 4.58122 | 11.0019 | 0.00185273 | PASS |
| `Knots_FourierSeries/5_1/knot.5_1u.fseries` | 7.75313 | 8.00173 | 3 | 3.24687 | 11.0074 | 0.00742555 | PASS |
| `knotplot/knot_T2.5/knot_T2.5.fseries` | -6.17428 | -6.00019 | 17 | 17.1743 | 11.0176 | 0.0176138 | PASS |
| `ideal:5:1:1` | -6.2938 | -5.99988 | 17 | 17.2938 | 11.0186 | 0.0185866 | PASS |

## T(2,7) target SL = 15

| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `ideal:7:1:1` | 9.18168 | 8.99999 | 6 | 5.81832 | 15.0019 | 0.00191313 | PASS |
| `knotplot/knot_7.1/knot_7.1.fseries` | 8.89497 | 9.00053 | 6 | 6.10503 | 15.0022 | 0.00224392 | PASS |
| `Knots_FourierSeries/7_1/knot.7_1.fseries` | 9.04451 | 9.00035 | 6 | 5.95549 | 15.0025 | 0.00250638 | PASS |
| `Knots_FourierSeries/7_1/knot.7_1p.fseries` | 9.39558 | 9.00172 | 6 | 5.60442 | 15.0044 | 0.00443105 | PASS |
| `knotplot/knot_T2.7/knot_T2.7.fseries` | -8.93998 | -9.00046 | 24 | 23.94 | 15.047 | 0.046989 | PASS |

## T(2,9) target SL = 19

| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `ideal:9:1:1` | 12.072 | 12.0001 | 7 | 6.928 | 19.0036 | 0.00362319 | PASS |
| `knotplot/knot_9.1/knot_9.1.fseries` | 11.6681 | 12.001 | 7 | 7.33189 | 19.0041 | 0.00407418 | PASS |

## T(2,11) target SL = 23

| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `ideal:K11a367` | -14.9489 | -15.0003 | 38 | 37.9489 | 23.1915 | 0.191532 | PASS |

## Twist / non-torus controls

| control | for q | Wr | Lk0 | Tw0 est | status | notes |
|---|---:|---:|---:|---:|---|---|
| `ideal:K11a247 (11_2_twist_control)` | 11 | 7.93943 | 8.00512 | 0.0656852 | NO_TARGET | Knot Atlas K11a247 / user-labelled 11_2 twist control; pq+1 torus target not applied |
| `Knots_FourierSeries/5_2/knot.5_2.fseries` | 5 | 4.81395 | 5.0007 | 0.18674 | NO_TARGET | fseries label matched 5_2 twist control; pq+1 torus target not applied |
| `Knots_FourierSeries/5_2/knot.5_2d.fseries` | 5 | 1.13404e-11 | -1.45599e-14 | -1.13549e-11 | NO_TARGET | fseries label matched 5_2 twist control; pq+1 torus target not applied |
| `Knots_FourierSeries/5_2/knot.5_2r.fseries` | 5 | 3.29752 | 2.8247 | -0.472819 | NO_TARGET | fseries label matched 5_2 twist control; pq+1 torus target not applied |
| `ideal:5:1:2 (5_2_twist_control)` | 5 | 4.54669 | 5.00066 | 0.453974 | NO_TARGET | Brian Gilbert ideal id 5:1:2 / user-labelled 5_2 twist control; pq+1 torus target not applied |
| `knotplot/knot_5.2.1/knot_5.2.1.fseries` | 5 | 0.539559 | 1.0008 | 0.46124 | NO_TARGET | fseries label matched 5_2 twist control; pq+1 torus target not applied |
| `knotplot/knot_5.2/knot_5.2.fseries` | 5 | 4.61056 | 5.00047 | 0.389908 | NO_TARGET | fseries label matched 5_2 twist control; pq+1 torus target not applied |

## Interpretation

`PASS` means the constructed framed ribbon numerically links near the target self-linking integer. It does **not** mean the Faddeev--Skyrme lattice relaxation is solved. This is the SST-native framed-helicity diagnostic, separated from the leaking Q_H relaxation pipeline.
