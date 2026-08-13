# SSTcore 0.8.28 — action–phase mass-shell clock

Adds `ActionPhaseAPI` / Node helpers for the relativistic mass-shell clock:

- `H = hypot(P c, E0)`
- `V = P c² / H`, `γ = H/E0`, `dτ/dT = E0/H`
- fixed-momentum internal phase rate `Ω = Ω0 E0/H`
- residual bundle for algebraic consistency

Reuses \(M_0(T)\) helpers from 0.8.26 and `CheckKind` from 0.8.27 for evidence labeling.
