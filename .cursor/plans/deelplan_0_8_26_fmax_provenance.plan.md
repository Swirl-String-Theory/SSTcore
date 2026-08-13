---
name: Deelplan 0.8.26 Fmax M0 ValueOrigin
overview: "Bump beide naar 0.8.26. Fmax 16π² + Rydberg; rho_horn; snapshot vs recompute (ValueOrigin); rho_f 2-sigfig; M0(T) bare-mass helpers (ownership hier; 0.8.28 hergebruikt)."
todos:
  - id: d826-ci-baseline
    content: "CI stap 1: pytest + npm test + test:parity groen"
    status: pending
  - id: d826-version-bump
    content: "Bump beide → 0.8.26"
    status: pending
  - id: d826-fmax-rho
    content: "Rydberg 16π² helper; rho_horn; F_SWIRL_MAX snapshot check"
    status: pending
  - id: d826-snapshot-recompute
    content: "ValueOrigin snapshot vs recompute + CanonicalValue/sig-fig"
    status: pending
  - id: d826-m0-helpers
    content: "bare_mass_* dimensionless L_tot; trefoil ref; tests/test_bare_mass.py"
    status: pending
  - id: d826-ci-regress
    content: "CI stap 3: regressie 100%"
    status: pending
  - id: d826-new-tests
    content: "CI stap 4–5: test_fmax_rydberg.py + test_canonical_snapshot.py + bare_mass + 100%"
    status: pending
  - id: d826-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.26: Fmax provenance and M0(T) helpers"
    status: pending
isProject: false
---

# Deelplan 0.8.26 — Fmax / rho / value-origin + \(M_0(T)\)

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_25_kam.plan.md](deelplan_0_8_25_kam.plan.md)  
**Next:** [deelplan_0_8_27_epistemica.plan.md](deelplan_0_8_27_epistemica.plan.md)  
**Target:** beide **"0.8.26"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — **\(M_0(T)\) ships hier**; 0.8.28 integreert alleen. Dit is **value-origin**, niet pipeline-provenance (0.8.23).

## Must-ship

```text
include/SST_Constants.h                 # F_SWIRL_MAX ongewijzigd 29.053507
src/canonical_constants.{h,cpp,_py,_node}.cpp  # snapshot/recompute/ValueOrigin
tests/test_fmax_rydberg.py
tests/test_canonical_snapshot.py
tests/test_bare_mass.py
```

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.26/`
- `SST-CANON/been_processed/sources/v0.8.26_patch_package/` (01 Fmax, 02 rho_horn, 03 M0/L, 04 rho_f)

## CI-poort

1. Baseline Python/Node/parity groen.
2. Constantenlaag, snapshot/recompute en \(M_0(T)\)-code zonder nieuwe tests.
3. Regressie 100% groen.
4. Precisie-, factor-2-, value-origin-, deprecation- en paritytests.
5. Final: docs, bindings, versievelden compleet.

## Scope

- Version bump → `0.8.26`.
- Bevestig `F_SWIRL_MAX = 29.053507` als canonieke snapshot.
- Rydberg \(16\pi^2 \hbar R_\infty^2 c/\alpha^5\)-helper.
- Snapshot vs recompute (~29.05351013) **gescheiden**.
- `rho_horn` i.p.v. `rho_calc`; \(\rho_f\) met `significant_figures=2`.
- \(M_0(T)=m_e L_{\rm tot}/4\) (dimensionloze `L_tot`).

**ValueOrigin + CanonicalValue** — zie structs in eerdere draft; interfaces `canonical_values()` / `recompute_from_primitives()` / `compare_snapshot_to_recomputed()`.

**Fmax guards:** \(16\pi^2\) slaagt; \(32\pi^2\) regressie faalt bewust; recompute residual wijzigt snapshot niet.

**Bare-mass:** `bare_mass_ratio_from_dimensionless_length`, `bare_mass_from_dimensionless_length`; trefoil \(L_{\rm tot}\simeq16.3716\Rightarrow M_0/m_e\simeq4.0929\) — AlgebraicIdentity / transparantie, geen massavoorspelling.

## Out of scope

- Action–phase; CheckKind/evidence-export; stille herkalibratie Fmax/\(\rho_f\).

## Exit

- Beide `0.8.26`; snapshot≠recompute; Fmax ongewijzigd; \(\rho_f\) 2-sigfig; `rho_horn` publiek; \(M_0(T)\) getest; CI/parity 100%.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.26: Fmax provenance and M0(T) helpers`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
