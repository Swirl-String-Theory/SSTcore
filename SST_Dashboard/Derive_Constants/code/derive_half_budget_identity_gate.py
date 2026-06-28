#!/usr/bin/env python3
"""
derive_half_budget_identity_gate.py

Attempt the next gate:

    M_total = E_eff/2.

Context
-------
Earlier scripts reduced the interior phase-Hessian gate to

    Lambda_phi = M_acc/(R-a)^2,

and derived the accessible-area factor

    M_acc = M_total (R-a)^2

if the phase budget is carried by accessible area.  Therefore the remaining
primitive gate is

    M_total = E_eff/2.

This script tests the only clean route found so far: a self-dual two-sector
quadratic budget.  If the finite cell has two conjugate sectors,

    phase sector      M_phi,
    pressure sector   M_p,

and if the reduced quadratic action is invariant under their exchange, then

    M_phi = M_p,

so

    E_eff = M_phi + M_p = 2 M_phi,

hence

    M_phi = E_eff/2.

This is a derivation inside the self-dual two-sector reduction.  It is NOT yet
a primitive derivation unless the phase/pressure exchange symmetry is itself
derived from the interior GP/SST dynamics.

Usage
-----
    python derive_half_budget_identity_gate.py --outdir outputs_half_budget_identity

Sensitivity:
    python derive_half_budget_identity_gate.py --gamma 1.05 --outdir outputs_half_budget_gamma105
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def sector_budget(Eeff: float, gamma: float):
    """gamma = M_phi/M_pressure."""
    M_pressure = Eeff/(1.0 + gamma)
    M_phi = gamma*Eeff/(1.0 + gamma)
    return M_phi, M_pressure


def evaluate(Eeff: float, gamma: float, L: float, R: float, a: float | None):
    if a is None:
        a = 1.0/(4.0*L)
    Racc = R-a
    f_area = (Racc/R)**2

    M_phi, M_pressure = sector_budget(Eeff, gamma)
    M_acc = M_phi*f_area
    Lambda = M_acc/(Racc*Racc)
    target = Eeff/2.0

    return {
        "E_eff": Eeff,
        "gamma_Mphi_over_Mpressure": gamma,
        "M_phi_total": M_phi,
        "M_pressure_total": M_pressure,
        "M_phi_over_Eeff": M_phi/Eeff,
        "target_Eeff_over_2": target,
        "M_phi_over_target": M_phi/target,
        "a": a,
        "R": R,
        "R_accessible": Racc,
        "accessible_area_fraction": f_area,
        "M_accessible": M_acc,
        "Lambda_phi": Lambda,
        "Lambda_over_target": Lambda/target,
        "relative_error_Lambda": Lambda/target - 1.0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--E-eff", type=float, default=274.0748756568)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--R", type=float, default=1.0)
    ap.add_argument("--a", type=float, default=None)
    ap.add_argument("--gamma", type=float, default=1.0, help="M_phi/M_pressure.")
    ap.add_argument("--tol", type=float, default=1e-12)
    ap.add_argument("--outdir", default="outputs_half_budget_identity")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    result = evaluate(args.E_eff, args.gamma, args.L_K, args.R, args.a)
    pass_half = abs(result["M_phi_over_target"] - 1.0) <= args.tol
    pass_lambda = abs(result["Lambda_over_target"] - 1.0) <= args.tol

    status = (
        "HALF_BUDGET_DERIVED_WITHIN_SELF_DUAL_TWO_SECTOR_MODEL"
        if pass_half and pass_lambda and abs(args.gamma-1.0) <= args.tol
        else "SENSITIVITY_OR_OPEN_SELF_DUALITY_GATE"
    )

    summary = [{**result, "status": status}]

    # Sensitivity over gamma.
    sens = []
    for gamma in [0.5, 0.75, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5, args.gamma]:
        r = evaluate(args.E_eff, gamma, args.L_K, args.R, args.a)
        sens.append({
            "gamma": gamma,
            "M_phi_over_Eeff": r["M_phi_over_Eeff"],
            "M_phi_over_target": r["M_phi_over_target"],
            "Lambda_over_target": r["Lambda_over_target"],
            "relative_error": r["relative_error_Lambda"],
        })

    theorem = [
        {
            "step": "two_sector_decomposition",
            "formula": "E_eff = M_phi + M_pressure",
            "status": "definition in two-sector reduced model",
        },
        {
            "step": "self_duality",
            "formula": "phase-pressure exchange symmetry implies M_phi = M_pressure",
            "status": "derived if exchange symmetry is a primitive symmetry",
        },
        {
            "step": "half_budget",
            "formula": "M_phi = E_eff/2",
            "status": "derived within self-dual two-sector model",
        },
        {
            "step": "accessible_area_projection",
            "formula": "M_acc = M_phi (R-a)^2/R^2",
            "status": "derived geometrically",
        },
        {
            "step": "interior_phase_Hessian",
            "formula": "Lambda_phi = M_acc/(R-a)^2 = E_eff/(2R^2)",
            "status": "conditional on self_duality; for R=1 gives E_eff/2",
        },
        {
            "step": "primitive_remaining_gate",
            "formula": "derive phase-pressure exchange symmetry from interior GP/SST equations",
            "status": "open beyond the reduced model",
        },
    ]

    write_csv(outdir/"half_budget_identity_summary.csv", summary)
    write_csv(outdir/"half_budget_identity_sensitivity.csv", sens)
    write_csv(outdir/"half_budget_identity_theorem_steps.csv", theorem)

    report = f"""# Half-budget identity gate

## Two-sector result

Assume the reduced finite-cell budget decomposes as

\\[
E_{{eff}}=M_\\phi+M_p.
\\]

Let

\\[
\\gamma=\\frac{{M_\\phi}}{{M_p}}.
\\]

Then

\\[
M_\\phi=\\frac{{\\gamma}}{{1+\\gamma}}E_{{eff}}.
\\]

For the self-dual value \\(\\gamma=1\\),

\\[
M_\\phi=\\frac{{E_{{eff}}}}{{2}}.
\\]

## Numerical result

\\[
E_{{eff}}={args.E_eff:.12g},
\\qquad
\\gamma={args.gamma:.12g}.
\\]

\\[
M_\\phi={result['M_phi_total']:.12g},
\\qquad
E_{{eff}}/2={result['target_Eeff_over_2']:.12g}.
\\]

With accessible-area projection,

\\[
M_{{acc}}=M_\\phi(R-a)^2
={result['M_accessible']:.12g}.
\\]

Then

\\[
\\Lambda_\\phi=\\frac{{M_{{acc}}}}{{(R-a)^2}}
={result['Lambda_phi']:.12g}.
\\]

Target ratio:

\\[
\\Lambda_\\phi/(E_{{eff}}/2)={result['Lambda_over_target']:.12g}.
\\]

Status: `{status}`.

## Interpretation

The half-budget identity is derived inside a self-dual two-sector
phase/pressure reduction.  The remaining primitive gate is to derive the
phase-pressure exchange symmetry from the interior GP/SST equations rather
than imposing \\(\\gamma=1\\).
"""
    (outdir/"half_budget_identity_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Half-budget identity from a self-dual two-sector reduction}
\label{app:half-budget-self-duality}

The accessible-area reduction leaves one primitive budget identity:
\[
  M_{\rm total}=\frac{E_{\rm eff}}{2}.
\]
A clean route is a two-sector decomposition of the finite-cell quadratic
budget,
\[
  E_{\rm eff}=M_\phi+M_p,
\]
where \(M_\phi\) is the phase sector and \(M_p\) the pressure/compression
sector.  Let
\[
  \gamma=\frac{M_\phi}{M_p}.
\]
Then
\[
  M_\phi=\frac{\gamma}{1+\gamma}E_{\rm eff}.
\]
If the reduced action is self-dual under exchange of the phase and pressure
sectors, then \(\gamma=1\), and hence
\[
  M_\phi=\frac{E_{\rm eff}}{2}.
\]
Combining this with the accessible-area projection
\[
  M_{\rm acc}=M_\phi\frac{(R-a)^2}{R^2}
\]
and the radial optimum
\[
  \Lambda_\phi=\frac{M_{\rm acc}}{(R-a)^2}
\]
gives, for the normalized cell \(R=1\),
\[
  \Lambda_\phi=\frac{E_{\rm eff}}{2}.
\]
Thus the half-budget identity is derived within the self-dual two-sector
finite-cell reduction.  The remaining primitive-equation task is to derive the
phase--pressure exchange symmetry from the interior GP/SST dynamics, rather
than postulating \(\gamma=1\).
"""
    (outdir/"half_budget_identity_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Half-budget identity gate")
    print("="*72)
    print(f"E_eff                 : {args.E_eff:.12g}")
    print(f"gamma                 : {args.gamma:.12g}")
    print(f"M_phi                 : {result['M_phi_total']:.12g}")
    print(f"E_eff/2               : {result['target_Eeff_over_2']:.12g}")
    print(f"Lambda_phi            : {result['Lambda_phi']:.12g}")
    print(f"Lambda/target         : {result['Lambda_over_target']:.12g}")
    print(f"status                : {status}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
