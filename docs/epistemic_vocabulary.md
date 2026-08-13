# Epistemic vocabulary (Canon v0.8.27+)

Closed `CheckKind` export strings:

| Enum | Export string |
|------|---------------|
| AlgebraicIdentity | `ALGEBRAIC_IDENTITY` |
| CalibratedClosure | `CALIBRATED_CLOSURE` |
| IndependentPrediction | `INDEPENDENT_PREDICTION` |
| NumericalConvergence | `NUMERICAL_CONVERGENCE` |
| ConditionalBridge | `CONDITIONAL_BRIDGE` |
| OpenResearchGate | `OPEN_RESEARCH_GATE` |
| SyntheticDiagnostic | `SYNTHETIC_DIAGNOSTIC` |

Notes:

- Pre-0.8.27 modules may still expose `epistemic_status` strings; map them with `check_kind_from_export_string`.
- `CertificateStatus::{Pass,Fail,...}` is a **gate outcome**, not an epistemic class.
- `PipelineCertificationStatus` (0.8.23) is provenance-chain status, not `CheckKind`.
- `ValueOrigin` (0.8.26) is constant/value provenance, not `CheckKind`.

Use `EvidenceReportAPI.write_evidence_report` so exports always include matching `sstcore_version` and `canon_version` (Optie A).
