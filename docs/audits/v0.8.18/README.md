# SSTcore v0.8.18 audit archive

Audit of SSTcore against SST Canon v0.8.18 after support-file integration.

| File | Description |
|---|---|
| [after_added_files_audit.md](after_added_files_audit.md) | Full formula coverage and verdict |
| [after_added_files_findings.tsv](after_added_files_findings.tsv) | P0/P1/P2 traceability |

## Applied in repo (P0 subset)

| ID | Change |
|---|---|
| P0-2 | `rho_fluid` → `7.0e-7` in `src/ab_initio_mass.h` |
| P0-3 | Chronos–Kelvin vorticity invariant + `swirl_clock_from_omega` with `4c²` |
| P0-4 | Time dilation default `c_vacuum`; `ab_initio_mass` passes `c_light` |
| P0-1 (partial) | `sst_extensions.cpp` include fix only; `../include/` layout retained |

Patch: [../patches/v0.8.18/0001-build-canon-fix.patch](../patches/v0.8.18/0001-build-canon-fix.patch)

P1/P2 items remain documented follow-up in the TSV.
