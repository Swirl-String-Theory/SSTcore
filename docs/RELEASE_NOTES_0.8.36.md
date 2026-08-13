# SSTcore 0.8.36 — Canon alignment through Maxwell stack

Brings package and canon pins to **0.8.36** (Optie A) on top of the completed 0.8.20–0.8.28 ladder.

## New modules (Python + Node)

| Edition | Module | Role |
|---------|--------|------|
| 0.8.29 | `ValueOriginAPI` guards | ρ_f 2-sf provenance, dependency guard, VAM no-go |
| 0.8.30 | `DensityOntologyAPI` | `ρ_sub`/`ρ_eff`/`J_ω`/`μ_ℓ`, dimensional validator |
| 0.8.31 | `RotorParticipationAPI` | `J_ω^rot`, `φ_dyn`, `ℓ_ρ,eq`, twist vs Kelvin bend |
| 0.8.32 | `ScalingAuditAPI` | `ρ_ref` legacy, `P_cal`/`P_open`/`P_ref`, A/B/C/Q/X |
| 0.8.33 | `WorldsheetGuardsAPI` | form-degree / non-identification guards |
| 0.8.34 | `IdealKnotRegimeAPI` | `ε_κ`, `ε_sep`, Moffatt–Ricca, LIA/KAM exclusion |
| 0.8.35 | `TransverseProjectorAPI` | `8π/3`, `R₀`, `R_SST`, twist bound, HR vs Gilbert |
| 0.8.36 | spectro / kinetic / falsifier / swirl-tonic | Maxwell stack diagnostics |

## Breaking note (0.8.32)

`7.0e-7` is **`ρ_ref` [LEGACY REFERENCE]**. `values().rho_f` still returns this value for backward compatibility but must not be treated as a calibrated primitive in `P_cal`.
