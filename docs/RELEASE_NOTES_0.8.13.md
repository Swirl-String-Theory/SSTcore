# Release Notes — SSTcore v0.8.13

Patch release aligning the shipped C++/Python core with **SST Canon v0.8.12** notation and constants, plus source-bundle provenance for audit trails.

Compared to **v0.8.12**, v0.8.13 applies the canon alignment changes that were previously documented only as external patches, adds regression tests, and ships those patches inside `SSTcore_source_v*.zip`.

---

## Changelog (v0.8.12 → v0.8.13)

### Canon alignment (applied in-tree)

- **CODATA-2018 α pin** — `SST::Constants::ALPHA` = `7.2973525693e-3` with provenance comments in `include/SST_Constants.h`
- **Chronos–Kelvin Ω vs ω** — `omega_from_swirl_clock` documents angular frequency Ω (unchanged); new **`vorticity_from_swirl_clock`** = 2Ω (Canon Sec. 2.9)
- **ρ notation** — **`rho_horn`** / **`horn_envelope_density()`** as canon aliases of `rho_core` / `core_density_closure` (horn-envelope density ≠ background `rho_m`)

### Tests & provenance

- New **`tests/test_canon_v0_8_12_alignment.py`** — α, vorticity = 2Ω, and `rho_horn` alias regressions
- Patch archive under [`docs/patches/v0.8.12/`](patches/v0.8.12/) (0001–0003 + combined `ALL` patch); included in source ZIP bundles
- Source ZIP builder: POSIX-safe path resolution for nested resource archives (Linux/macOS CI)

### Packaging

- Package version **0.8.13** in `setup.py` and `src/SSTcore/__init__.py`
- Default output: `dist/SSTcore_source_v0.8.13.zip`

---

## Migration

No breaking API changes. Existing code using `omega_from_swirl_clock`, `rho_core`, or `core_density_closure` behaves as before. Prefer the new canon names where traceability to SST Canon v0.8.12 matters.

---

## Summary

**SSTcore v0.8.13** is the recommended PyPI/source bundle for SST Canon v0.8.12 numerical work: alignment patches are applied, tested, and reproducible from the shipped patch archive.
