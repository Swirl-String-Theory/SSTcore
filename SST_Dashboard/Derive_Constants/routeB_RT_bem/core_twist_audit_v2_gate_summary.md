# Core-Holonomy v2 audit summary

Generated: 2026-06-25 19:33:38

## Canon-candidate proof stack

```text
[DERIVED]              |SL_torus(T(p,q))| = p q for canonical torus-surface framing.
[FR-GATE / CONDITIONAL] If core-frame winding realizes the nontrivial FR loop, n_core is odd.
[KINEMATIC IDENTITY]   Omega_core*T_core = 2π by SST core definitions.
[ATTACHMENT / OPEN]    Local core cycle must attach globally as closed-knot framing holonomy.
[ENERGY / CONDITIONAL] Given attachment and C_T>0, E_twist selects n_core=chi.
[CONDITIONAL]          SL_phys(T(p,q)) = SL_torus(T(p,q)) + chi.
```

## Canonical core-cycle constants

The local core cycle is kinematic, not by itself a global holonomy theorem.

| quantity | value |
|---|---:|
| `||v_swirl||` | 1.093845630000e+06 m/s |
| `r_c` | 1.408970170000e-15 m |
| `Omega_core = ||v_swirl||/r_c` | 7.763440655383e+20 s^-1 |
| `T_core = 2π r_c/||v_swirl||` | 8.093299847437e-21 s |
| `Omega_core*T_core/(2π)` | 1.000000000000 turns |
| `omega_vorticity*T_core/(2π)` | 2.000000000000 vorticity-turns |

Important: the framing angle integrates angular velocity `Omega_core`, not vorticity `omega_core=2 Omega_core`; equivalently `dtheta_frame = 0.5 omega_core dt`.

## M0--M5 scenario matrix

Gate rows: **162**. Counts: `{'M0_NONE:BOSONIC_DEFAULT': 27, 'M1_FR_ONLY:LOWEST_ODD_SELECTED': 27, 'M2_CANON_CYCLE_LOCAL_ONLY:LOCAL_IDENTITY_ONLY': 27, 'M3_CANON_CYCLE_ATTACHED_MATTER:CONDITIONAL_CANON_CANDIDATE': 27, 'M4_CANON_CYCLE_ATTACHED_ANTIMATTER:CONDITIONAL_MIRROR_SECTOR': 27, 'M5_TWOOMEGA_TRANSIT:PASSIVE_ADVECTION_FAILS': 27}`

| curve | scenario | parity | holonomy | attachment | chi | center | selected n | degenerate | |SL_phys| | status |
|---|---|---|---|---|---|---:|---:|---|---:|---|
| `analytic:T(2,3)` | `M0_NONE` | none | none | none | unsigned | 0 | 0 |  | 6 | BOSONIC_DEFAULT |
| `analytic:T(2,3)` | `M1_FR_ONLY` | odd | none | none | unsigned | 0 |  | -1,1 |  | LOWEST_ODD_SELECTED |
| `analytic:T(2,3)` | `M2_CANON_CYCLE_LOCAL_ONLY` | none | canon_core_cycle | none | unsigned |  |  |  |  | LOCAL_IDENTITY_ONLY |
| `analytic:T(2,3)` | `M3_CANON_CYCLE_ATTACHED_MATTER` | odd | canon_core_cycle | global | matter | 1 | 1 |  | 7 | CONDITIONAL_CANON_CANDIDATE |
| `analytic:T(2,3)` | `M4_CANON_CYCLE_ATTACHED_ANTIMATTER` | odd | canon_core_cycle | global | antimatter | -1 | -1 |  | 7 | CONDITIONAL_MIRROR_SECTOR |
| `analytic:T(2,3)` | `M5_TWOOMEGA_TRANSIT` | none | twoomega_transit | passive_transit | unsigned | 2.501 | 3 |  | 3 | PASSIVE_ADVECTION_FAILS |
| `analytic:T(2,5)` | `M0_NONE` | none | none | none | unsigned | 0 | 0 |  | 10 | BOSONIC_DEFAULT |
| `analytic:T(2,5)` | `M1_FR_ONLY` | odd | none | none | unsigned | 0 |  | -1,1 |  | LOWEST_ODD_SELECTED |
| `analytic:T(2,5)` | `M2_CANON_CYCLE_LOCAL_ONLY` | none | canon_core_cycle | none | unsigned |  |  |  |  | LOCAL_IDENTITY_ONLY |
| `analytic:T(2,5)` | `M3_CANON_CYCLE_ATTACHED_MATTER` | odd | canon_core_cycle | global | matter | 1 | 1 |  | 11 | CONDITIONAL_CANON_CANDIDATE |
| `analytic:T(2,5)` | `M4_CANON_CYCLE_ATTACHED_ANTIMATTER` | odd | canon_core_cycle | global | antimatter | -1 | -1 |  | 11 | CONDITIONAL_MIRROR_SECTOR |
| `analytic:T(2,5)` | `M5_TWOOMEGA_TRANSIT` | none | twoomega_transit | passive_transit | unsigned | 2.501 | 3 |  | 7 | PASSIVE_ADVECTION_FAILS |
| `analytic:T(2,7)` | `M0_NONE` | none | none | none | unsigned | 0 | 0 |  | 14 | BOSONIC_DEFAULT |
| `analytic:T(2,7)` | `M1_FR_ONLY` | odd | none | none | unsigned | 0 |  | -1,1 |  | LOWEST_ODD_SELECTED |
| `analytic:T(2,7)` | `M2_CANON_CYCLE_LOCAL_ONLY` | none | canon_core_cycle | none | unsigned |  |  |  |  | LOCAL_IDENTITY_ONLY |
| `analytic:T(2,7)` | `M3_CANON_CYCLE_ATTACHED_MATTER` | odd | canon_core_cycle | global | matter | 1 | 1 |  | 15 | CONDITIONAL_CANON_CANDIDATE |
| `analytic:T(2,7)` | `M4_CANON_CYCLE_ATTACHED_ANTIMATTER` | odd | canon_core_cycle | global | antimatter | -1 | -1 |  | 15 | CONDITIONAL_MIRROR_SECTOR |
| `analytic:T(2,7)` | `M5_TWOOMEGA_TRANSIT` | none | twoomega_transit | passive_transit | unsigned | 2.501 | 3 |  | 11 | PASSIVE_ADVECTION_FAILS |
| `analytic:T(2,9)` | `M0_NONE` | none | none | none | unsigned | 0 | 0 |  | 18 | BOSONIC_DEFAULT |
| `analytic:T(2,9)` | `M1_FR_ONLY` | odd | none | none | unsigned | 0 |  | -1,1 |  | LOWEST_ODD_SELECTED |
| `analytic:T(2,9)` | `M2_CANON_CYCLE_LOCAL_ONLY` | none | canon_core_cycle | none | unsigned |  |  |  |  | LOCAL_IDENTITY_ONLY |
| `analytic:T(2,9)` | `M3_CANON_CYCLE_ATTACHED_MATTER` | odd | canon_core_cycle | global | matter | 1 | 1 |  | 19 | CONDITIONAL_CANON_CANDIDATE |
| `analytic:T(2,9)` | `M4_CANON_CYCLE_ATTACHED_ANTIMATTER` | odd | canon_core_cycle | global | antimatter | -1 | -1 |  | 19 | CONDITIONAL_MIRROR_SECTOR |
| `analytic:T(2,9)` | `M5_TWOOMEGA_TRANSIT` | none | twoomega_transit | passive_transit | unsigned | 2.501 | 3 |  | 15 | PASSIVE_ADVECTION_FAILS |
| `analytic:T(2,11)` | `M0_NONE` | none | none | none | unsigned | 0 | 0 |  | 22 | BOSONIC_DEFAULT |
| `analytic:T(2,11)` | `M1_FR_ONLY` | odd | none | none | unsigned | 0 |  | -1,1 |  | LOWEST_ODD_SELECTED |
| `analytic:T(2,11)` | `M2_CANON_CYCLE_LOCAL_ONLY` | none | canon_core_cycle | none | unsigned |  |  |  |  | LOCAL_IDENTITY_ONLY |
| `analytic:T(2,11)` | `M3_CANON_CYCLE_ATTACHED_MATTER` | odd | canon_core_cycle | global | matter | 1 | 1 |  | 23 | CONDITIONAL_CANON_CANDIDATE |
| `analytic:T(2,11)` | `M4_CANON_CYCLE_ATTACHED_ANTIMATTER` | odd | canon_core_cycle | global | antimatter | -1 | -1 |  | 23 | CONDITIONAL_MIRROR_SECTOR |
| `analytic:T(2,11)` | `M5_TWOOMEGA_TRANSIT` | none | twoomega_transit | passive_transit | unsigned | 2.501 | 3 |  | 19 | PASSIVE_ADVECTION_FAILS |

## Interpretation

```text
M0_NONE: no FR and no holonomy -> n_core=0, bosonic/default sector.
M1_FR_ONLY: odd FR sector -> lowest odd pair n_core=±1, but no matter/antimatter sign.
M2_CANON_CYCLE_LOCAL_ONLY: Omega*T=2π is local only; no global n_core selected.
M3_CANON_CYCLE_ATTACHED_MATTER: with FR+attachment+C_T>0 -> n_core=+1.
M4_CANON_CYCLE_ATTACHED_ANTIMATTER: with FR+attachment+C_T>0 -> n_core=-1.
M5_TWOOMEGA_TRANSIT: passive transit noninteger center -> not a valid integer core-twist theorem.
```

## Audit conclusion

The +1 core twist is not inserted as a target in M3. It is selected only after three explicit gates: FR parity identification, global core-cycle attachment, and positive twist stiffness. The attachment lemma remains the main open/load-bearing step.
