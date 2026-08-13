---
name: Deelplan 0.8.28 Action Phase
overview: "Bump beide naar 0.8.28. action_phase module: mass-shell H, V, gamma, proper-time, internal_phase_rate_at_fixed_momentum, residuals, fixed-P guard."
todos:
  - id: d828-ci-baseline
    content: "CI stap 1: Python + Node groen"
    status: pending
  - id: d828-version-bump
    content: "Bump beide → 0.8.28"
    status: pending
  - id: d828-action-phase-cpp
    content: "include/sst_action_phase.h + src/sst_action_phase.cpp (hypot, validation)"
    status: pending
  - id: d828-bind
    content: "sst_action_phase_py/node + bind in module_sst/module_node + CMake/setup"
    status: pending
  - id: d828-ci-regress
    content: "CI stap 3: regressie 100% (incl. versie-pins 0.8.28)"
    status: pending
  - id: d828-new-tests
    content: "CI stap 4–5: test_action_phase.py/.js (+ optional cpp) + BINDING_COVERAGE + 100%"
    status: pending
  - id: d828-docs-coverage
    content: "BINDING_COVERAGE + RELEASE_NOTES_0.8.28.md"
    status: pending
  - id: d828-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.28: action–phase mass-shell clock"
    status: pending
isProject: false
---

# Deelplan 0.8.28 — Action–phase mass-shell clock

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** [deelplan_0_8_27_epistemica.plan.md](deelplan_0_8_27_epistemica.plan.md)  
**Next:** optioneel research-followup (blijft 0.8.28)  
**Target:** beide **"0.8.28"**  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md) — \(M_0(T)\) **hergebruik uit 0.8.26**; epistemic via `CheckKind` uit 0.8.27.

## Canon-bronnen

- `SST-CANON/been_processed/v0.8.28/`
- `SST-CANON/been_processed/sources/v0.8.28_action_phase_clock/` (+ AUDIT)

## CI-poort


1. Baseline Python/Node/parity groen; evidence bewaren.
2. C++-, Python- en Node-productiecode plus wiring toevoegen; **geen nieuwe tests**.
3. Regressie: bestaande suite 100% groen, inclusief versie-pins `0.8.28`.
4. Nieuwe analytische, residual-, fixed-\(P\)-, tegenmodel-, foutpad- en paritytests.
5. Final: evidence-export, binding coverage, docs en volledige CI groen.

## Scope — must-ship API


Bestanden:

```text
include/sst_action_phase.h
src/sst_action_phase.cpp
src/sst_action_phase_py.cpp
src/sst_action_phase_node.cpp
tests/test_action_phase.cpp
tests/test_action_phase.py
tests/test_action_phase.js
```

Functies:

1. `mass_shell_hamiltonian(P, E0, c)` — `std::hypot(P*c, E0)`
2. `velocity_from_mass_shell` — \(V = P c^2 / H\)
3. `gamma_from_mass_shell` — \(H/E_0\)
4. `proper_time_rate` — \(E_0/H\)
5. `internal_phase_rate_at_fixed_momentum` — \(\Omega_0 E_0/H\)
6. `action_phase_residuals` → `ActionPhaseResiduals`

**Centrale Hamiltoniaan**

\[
\boxed{
H(P,I)=\sqrt{P^2c^2+E_0^2(I)}
}
\]

met:

\[
V=\frac{Pc^2}{H},
\qquad
\gamma=\frac{H}{E_0},
\qquad
\frac{d\tau}{dT}=\frac{E_0}{H},
\qquad
\Omega(P,I)=\frac{\Omega_0(I)}{\gamma}.
\]

**Inputvalidatie**

- weiger NaN en niet-finite waarden;
- \(E_0>0\);
- \(c>0\);
- \(P\in\mathbb R\);
- controleer \(0<E_0/H\leq1\).

Gebruik `std::hypot` om overflow bij grote impuls te vermijden.

**Fixed-\(P\)-contract**

De publieke naam bevat expliciet `at_fixed_momentum`. Documenteer:

\[
\left.\frac{\partial H}{\partial I}\right|_P
=
\frac{E_0}{H}\Omega_0.
\]

Geen ambigue alias toevoegen.

**Residualstruct**

```cpp
struct ActionPhaseResiduals {
    double delta_shell;
    double delta_velocity;
    double delta_phase;
    double delta_shape_separability;
};
```

Gebruik genormaliseerde residuals voor:

\[
H^2-P^2c^2-E_0^2,
\]

\[
V-\frac{Pc^2}{H},
\]

\[
\Omega-\frac{E_0}{H}\Omega_0,
\]

en, bij een vormvariabele \(q\):

\[
\partial_qH-\frac{E_0}{H}\partial_qE_0.
\]

**Discriminerend tegenmodel**

Test naast de separabele mass-shell:

\[
H_{\rm coupled}
=
\sqrt{P^2c^2+E_0^2(I,q)}
+\varepsilon P^2 f(q).
\]

De shape-residual moet dan aantoonbaar niet nul blijven.

**Fixed-\(V\)-wrongness guard**

Een bewuste fouttest reproduceert:

\[
\frac{\Omega_{\rm wrong}}{\Omega_{\rm correct}}-1
=
\gamma^2-1.
\]

Hiermee wordt voorkomen dat een latere refactor de constraint verwisselt.

**Limiettests**

\[
P=0\Rightarrow V=0,\ \gamma=1,\ d\tau/dT=1,
\]

\[
|P|\to\infty\Rightarrow |V|\to c,\ d\tau/dT\to0.
\]

Test positieve en negatieve impuls en een rooster \(V/c=0.01\ldots0.99\).

**\(M_0(T)\)-integratie**

De helpers uit `0.8.26` worden hergebruikt; geen duplicaatfunctie. Alleen regressie, import en evidence-koppeling.

**Epistemische status**

Exporteer via `CheckKind` / exportstrings:

- `CONDITIONAL_BRIDGE` (menselijke toelichting: OrthodoxForm / conditional mass-shell route)
- `OPEN_RESEARCH_GATE` (toelichting: NotAnIndependentSSTDerivation — geen finite-core \(E_0(I)\)-afleiding)

**Docs / coverage (stap 2 of 5)**

- Update `docs/BINDING_COVERAGE.md` + binding_manifest
- `docs/RELEASE_NOTES_0.8.28.md`

## Out of scope (later, blijft 0.8.28)


- Resolved \(E_0[\mathbf X]\)-functionaal; surrogate blijft toegestaan.
- Constructie van een concrete interne actie uit een opgeloste vortexmode.
- Preferred-frame/boostscan.
- Biot–Savart \(N\to32000\)-sweep.
- Brede NumPy-vectorisatie; dunne wrappers mogen wel.
- Afplatting, stretching of uniforme core-thinning als gevolg van translatie.

## Exit


- Beide versies `0.8.28`.
- Mass-shell-, snelheid-, proper-time- en fasehelpers zijn beschikbaar in C++, Python en Node.
- Residuals liggen onder vastgelegde toleranties.
- Fixed-\(P\) is zichtbaar in API, docs en tests.
- De fixed-\(V\)-foutguard reproduceert \(\gamma^2-1\).
- Het gekoppelde tegenmodel toont dat de shape-test niet triviaal is.
- \(M_0(T)\)-helpers worden zonder duplicatie hergebruikt.
- Evidence-export bevat `ConditionalBridge` en geen overclaim.
- `BINDING_COVERAGE.md` bijgewerkt; volledige CI en parity 100% groen.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.28: action–phase mass-shell clock`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
