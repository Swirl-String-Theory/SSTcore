# Attachment Lemma audit summary

## Purpose

This audit asks whether a local SST core cycle can be promoted to a global closed-knot framing holonomy.

```text
[TARGET]  Hol(A_core)/(2π) = chi = ±1
[OPEN]    The equality between local core period and global ribbon holonomy is the Attachment Lemma.
```

## Canonical core constants

| quantity | value |
|---|---:|
| `||v_swirl||` | 1.093845630000e+06 m/s |
| `r_c` | 1.408970170000e-15 m |
| `Omega_core = ||v_swirl||/r_c` | 7.763440655383e+20 s^-1 |
| `T_core = 2π r_c/||v_swirl||` | 8.093299847437e-21 s |
| `Omega_core*T_core/(2π)` | 1.000000000000 turns |
| `omega_vorticity*T_core/(2π)` | 2.000000000000 vorticity-turns |

The framing angle integrates angular velocity, not vorticity: `dtheta_frame = Omega_core dt = 0.5 omega_core dt`.

## Proof-stack status

```text
[DERIVED]              Canonical torus-surface framing: |SL_torus(T(p,q))| = p q.
[FR-GATE / CONDITIONAL] Core-frame winding must represent the nontrivial FR loop to force odd n_core.
[KINEMATIC IDENTITY]   Omega_core*T_core = 2π locally.
[ATTACHMENT / OPEN]    Local core cycle must attach globally as framed-knot holonomy.
[ENERGY / CONDITIONAL] Given global attachment and C_T>0, n_core=chi is selected.
[CONDITIONAL]          SL_phys(T(p,q)) = SL_torus(T(p,q)) + chi.
```

## Row counts

Geometry rows: **16**
Attachment result rows: **144**
Model counts: `{'A0_FREE_NONE': 16, 'A1_FR_ONLY': 16, 'A2_CANON_CYCLE_LOCAL_ONLY': 16, 'A3_CANON_ATTACHED_MATTER': 16, 'A4_CANON_ATTACHED_ANTIMATTER': 16, 'A5_PASSIVE_TRANSIT_NONE': 16, 'A6_PASSIVE_TRANSIT_FR_ODD': 16, 'A7_Q_DEPENDENT_LOCK_MATTER': 16, 'A8_NOISY_LOCK_MATTER': 16}`
Status counts: `{'BOSONIC_DEFAULT': 16, 'FR_ODD_SELECTED_NO_SIGN': 16, 'ATTACHMENT_REQUIRED': 16, 'CONDITIONAL_CANON_CANDIDATE': 16, 'CONDITIONAL_MIRROR_SECTOR': 16, 'PASSIVE_ADVECTION_FAILS': 32, 'Q_DEPENDENT_DIAGNOSTIC': 16, 'NOISY_STABILITY_DIAGNOSTIC': 16}`
Geometry-quality counts: `{'CANONICAL_GEOMETRY': 144}`

## Model catalogue

| model_id | parity | connection | attachment | chirality | center_kind | epistemic_status |
|---|---|---|---|---|---|---|
| A0_FREE_NONE | none | none | none | unsigned | zero | FREE_FRAME_NO_ATTACHMENT |
| A1_FR_ONLY | odd | fr_only | none | unsigned | zero | FR_PARITY_ONLY_LOWEST_ODD |
| A2_CANON_CYCLE_LOCAL_ONLY | none | canon_core_cycle | local_only | unsigned | none | LOCAL_IDENTITY_ONLY_ATTACHMENT_REQUIRED |
| A3_CANON_ATTACHED_MATTER | odd | canon_core_cycle | global | matter | chi | ATTACHED_MATTER_CONDITIONAL |
| A4_CANON_ATTACHED_ANTIMATTER | odd | canon_core_cycle | global | antimatter | chi | ATTACHED_ANTIMATTER_CONDITIONAL |
| A5_PASSIVE_TRANSIT_NONE | none | passive_transit | passive_transit | unsigned | passive | PASSIVE_ADVECTION_FAILS |
| A6_PASSIVE_TRANSIT_FR_ODD | odd | passive_transit | passive_transit | unsigned | passive | PASSIVE_ADVECTION_FAILS_EVEN_WITH_FR |
| A7_Q_DEPENDENT_LOCK_MATTER | odd | q_dependent_lock | global | matter | q_dependent | Q_DEPENDENT_LOCK_DIAGNOSTIC |
| A8_NOISY_LOCK_MATTER | odd | noisy_lock | global | matter | noisy | NOISY_LOCK_STABILITY_DIAGNOSTIC |

## Preview: canonical analytic/torus rows

| curve | model_id | center_turns | selected_n_core | sl_phys_abs | exact_pq_plus_1 | status |
|---|---|---|---|---|---|---|
| analytic:T(2,3) | A0_FREE_NONE | 0 | 0 | 6 | NO | BOSONIC_DEFAULT |
| analytic:T(2,3) | A1_FR_ONLY | 0 | -1,1 | 7,7 | YES | FR_ODD_SELECTED_NO_SIGN |
| analytic:T(2,3) | A2_CANON_CYCLE_LOCAL_ONLY |  |  |  |  | ATTACHMENT_REQUIRED |
| analytic:T(2,3) | A3_CANON_ATTACHED_MATTER | 1 | 1 | 7 | YES | CONDITIONAL_CANON_CANDIDATE |
| analytic:T(2,3) | A4_CANON_ATTACHED_ANTIMATTER | -1 | -1 | 7 | YES | CONDITIONAL_MIRROR_SECTOR |
| analytic:T(2,3) | A5_PASSIVE_TRANSIT_NONE | 2.501 | 3 | 9 | NO | PASSIVE_ADVECTION_FAILS |
| analytic:T(2,5) | A0_FREE_NONE | 0 | 0 | 10 | NO | BOSONIC_DEFAULT |
| analytic:T(2,5) | A1_FR_ONLY | 0 | -1,1 | 11,11 | YES | FR_ODD_SELECTED_NO_SIGN |
| analytic:T(2,5) | A2_CANON_CYCLE_LOCAL_ONLY |  |  |  |  | ATTACHMENT_REQUIRED |
| analytic:T(2,5) | A3_CANON_ATTACHED_MATTER | 1 | 1 | 11 | YES | CONDITIONAL_CANON_CANDIDATE |
| analytic:T(2,5) | A4_CANON_ATTACHED_ANTIMATTER | -1 | -1 | 11 | YES | CONDITIONAL_MIRROR_SECTOR |
| analytic:T(2,5) | A5_PASSIVE_TRANSIT_NONE | 2.501 | 3 | 13 | NO | PASSIVE_ADVECTION_FAILS |
| analytic:T(2,7) | A0_FREE_NONE | 0 | 0 | 14 | NO | BOSONIC_DEFAULT |
| analytic:T(2,7) | A1_FR_ONLY | 0 | -1,1 | 15,15 | YES | FR_ODD_SELECTED_NO_SIGN |
| analytic:T(2,7) | A2_CANON_CYCLE_LOCAL_ONLY |  |  |  |  | ATTACHMENT_REQUIRED |
| analytic:T(2,7) | A3_CANON_ATTACHED_MATTER | 1 | 1 | 15 | YES | CONDITIONAL_CANON_CANDIDATE |
| analytic:T(2,7) | A4_CANON_ATTACHED_ANTIMATTER | -1 | -1 | 15 | YES | CONDITIONAL_MIRROR_SECTOR |
| analytic:T(2,7) | A5_PASSIVE_TRANSIT_NONE | 2.501 | 3 | 17 | NO | PASSIVE_ADVECTION_FAILS |
| analytic:T(2,9) | A0_FREE_NONE | 0 | 0 | 18 | NO | BOSONIC_DEFAULT |
| analytic:T(2,9) | A1_FR_ONLY | 0 | -1,1 | 19,19 | YES | FR_ODD_SELECTED_NO_SIGN |
| analytic:T(2,9) | A2_CANON_CYCLE_LOCAL_ONLY |  |  |  |  | ATTACHMENT_REQUIRED |
| analytic:T(2,9) | A3_CANON_ATTACHED_MATTER | 1 | 1 | 19 | YES | CONDITIONAL_CANON_CANDIDATE |
| analytic:T(2,9) | A4_CANON_ATTACHED_ANTIMATTER | -1 | -1 | 19 | YES | CONDITIONAL_MIRROR_SECTOR |
| analytic:T(2,9) | A5_PASSIVE_TRANSIT_NONE | 2.501 | 3 | 21 | NO | PASSIVE_ADVECTION_FAILS |
| analytic:T(2,11) | A0_FREE_NONE | 0 | 0 | 22 | NO | BOSONIC_DEFAULT |
| analytic:T(2,11) | A1_FR_ONLY | 0 | -1,1 | 23,23 | YES | FR_ODD_SELECTED_NO_SIGN |
| analytic:T(2,11) | A2_CANON_CYCLE_LOCAL_ONLY |  |  |  |  | ATTACHMENT_REQUIRED |
| analytic:T(2,11) | A3_CANON_ATTACHED_MATTER | 1 | 1 | 23 | YES | CONDITIONAL_CANON_CANDIDATE |
| analytic:T(2,11) | A4_CANON_ATTACHED_ANTIMATTER | -1 | -1 | 23 | YES | CONDITIONAL_MIRROR_SECTOR |
| analytic:T(2,11) | A5_PASSIVE_TRANSIT_NONE | 2.501 | 3 | 25 | NO | PASSIVE_ADVECTION_FAILS |

## Interpretation

```text
A0_FREE_NONE: no FR and no attachment -> n_core=0, default/bosonic sector.
A1_FR_ONLY: FR odd parity -> n_core=±1, but no matter/antimatter sign or global holonomy theorem.
A2_CANON_CYCLE_LOCAL_ONLY: Omega*T=2π is local only; attachment is still required.
A3_CANON_ATTACHED_MATTER: FR + attachment + C_T>0 + chi=+1 -> n_core=+1.
A4_CANON_ATTACHED_ANTIMATTER: FR + attachment + C_T>0 + chi=-1 -> n_core=-1.
A5/A6_PASSIVE_TRANSIT: passive non-integer transit selects the wrong integer sector; it is not the pq+1 mechanism.
A7/A8 perturbation models, when enabled, are stability diagnostics only; exact Canon requires r(q)=chi, not merely near chi.
```

## Audit conclusion

The Attachment Lemma remains the load-bearing open step.  The candidate mechanism is not 'more pq+1 fitting'; it is the construction of a physical U(1) core-phase connection whose closed-knot holonomy is exactly `2π chi`.
