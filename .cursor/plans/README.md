# SSTcore Canon upgrade — plan index

Hoofdplan: [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
Gedeelde regels: [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md)

Voer deelplannen **strikt in volgorde** uit. Elk deelplan volgt de CI-poort in SHARED_CONVENTIONS, inclusief **stap 6: aparte git-commit** (geen multi-deelplan commits).

| Order | File | Version | Kern |
| --- | --- | --- | --- |
| 0 | [deelplan_0_baseline.plan.md](deelplan_0_baseline.plan.md) | 0.8.19 | Versiesync + baseline CI |
| 1 | [deelplan_0_8_20_geometry_contact.plan.md](deelplan_0_8_20_geometry_contact.plan.md) | 0.8.20 | Geometry + contact/Chronos + `CertificateStatus` |
| 2 | [deelplan_0_8_21_certification_biot.plan.md](deelplan_0_8_21_certification_biot.plan.md) | 0.8.21 | Ridgerunner/Biot gates |
| 3 | [deelplan_0_8_22_spacetime_qss.plan.md](deelplan_0_8_22_spacetime_qss.plan.md) | 0.8.22 | Spacetime + QSS (string epistemic tot 27) |
| 4 | [deelplan_0_8_23_provenance.plan.md](deelplan_0_8_23_provenance.plan.md) | 0.8.23 | Pipeline provenance (`PipelineCertificationStatus`) |
| 5 | [deelplan_0_8_24_core_torsion.plan.md](deelplan_0_8_24_core_torsion.plan.md) | 0.8.24 | Core–torsion factor-2 + link-gate |
| 6 | [deelplan_0_8_25_kam.plan.md](deelplan_0_8_25_kam.plan.md) | 0.8.25 | KAM stage-1 |
| 7 | [deelplan_0_8_26_fmax_provenance.plan.md](deelplan_0_8_26_fmax_provenance.plan.md) | 0.8.26 | Fmax/rho/`M0(T)` + value-origin |
| 8 | [deelplan_0_8_27_epistemica.plan.md](deelplan_0_8_27_epistemica.plan.md) | 0.8.27 | `CheckKind` + evidence-export |
| 9 | [deelplan_0_8_28_action_phase.plan.md](deelplan_0_8_28_action_phase.plan.md) | 0.8.28 | Action–phase mass-shell |

Na 0.8.28: research-followup blijft versie **0.8.28** (geen major bump).  
**Commits:** één commit per deelplan — zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) § Git.
