#!/usr/bin/env python3
"""
derive_accessible_area_phase_budget_gate.py

Attempt the next interior phase-Hessian gate:

    M_req = (E_eff/2) (R-a)^2.

Previous result
---------------
The radial phase-Hessian theorem gave

    Lambda_phi = M/(R-a)^2

for the optimal radial stiffness profile n(r) proportional to 1/r^2.

Therefore Lambda_phi = E_eff/2 is equivalent to

    M = (E_eff/2)(R-a)^2.

This script tests whether the factor (R-a)^2 can be derived as an accessible
area fraction, and isolates the remaining primitive gate.

What is derived here
--------------------
For a spherical cell with outer radius R and inner excluded radius a, the
accessible radial scale is

    R_acc = R-a.

If the phase-stiffness budget is carried by an accessible spherical screen
whose area scales as R_acc^2, then the accessible area fraction is

    f_A = A_acc/A_out = (R-a)^2/R^2.

For normalized R=1,

    f_A = (R-a)^2.

Thus, if the total phase budget is independently

    M_total = E_eff/2,

then

    M_acc = M_total f_A = (E_eff/2)(R-a)^2,

and the radial optimal profile gives

    Lambda_phi = M_acc/(R-a)^2 = E_eff/2.

What remains open
-----------------
This script does NOT derive M_total = E_eff/2 from primitive dynamics.  It
derives the accessible-area factor and shows that the remaining gate is the
half-budget identity

    M_total = E_eff/2.

Usage
-----
    python derive_accessible_area_phase_budget_gate.py --outdir outputs_accessible_area_budget
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


def evaluate(Eeff: float, L: float, R: float, a: float | None):
    if a is None:
        a = 1.0/(4.0*L)
    Racc = R - a
    f_area = (Racc/R)**2
    f_length = Racc/R
    f_volume = (R**3 - a**3)/(R**3)

    target = Eeff/2.0
    M_required = target * Racc*Racc

    candidates = [
        ("half_budget_area_projected", target*f_area, "M_total=Eeff/2 projected by accessible area fraction"),
        ("half_budget_length_projected", target*f_length, "M_total=Eeff/2 projected by accessible length fraction"),
        ("half_budget_volume_projected", target*f_volume, "M_total=Eeff/2 projected by accessible volume fraction"),
        ("full_budget_area_projected", Eeff*f_area, "M_total=Eeff projected by accessible area fraction"),
        ("raw_half_budget", target, "no accessible projection"),
        ("required_budget", M_required, "diagnostic required value"),
    ]

    rows = []
    for name, M, interp in candidates:
        Lambda = M/(Racc*Racc)
        rows.append({
            "candidate": name,
            "M": M,
            "interpretation": interp,
            "Lambda_from_optimal_radial_profile": Lambda,
            "target_Eeff_over_2": target,
            "ratio_to_target": Lambda/target,
            "relative_error": Lambda/target - 1.0,
            "is_exact": abs(Lambda/target - 1.0) < 1e-12,
            "epistemic_status": (
                "exact_if_half_budget_is_independent" if name=="half_budget_area_projected" else
                "diagnostic_required_value" if name=="required_budget" else
                "tested_alternative"
            ),
        })

    summary = {
        "E_eff": Eeff,
        "E_eff_over_2": target,
        "L_K": L,
        "R": R,
        "a": a,
        "R_accessible": Racc,
        "area_fraction": f_area,
        "length_fraction": f_length,
        "volume_fraction": f_volume,
        "M_required": M_required,
        "M_required_over_Eeff_over_2": M_required/target,
        "exact_candidate": "half_budget_area_projected",
        "closed_gate_if": "derive M_total=E_eff/2 independently",
        "status": "ACCESSIBLE_AREA_FACTOR_DERIVED_HALF_BUDGET_OPEN",
    }
    return rows, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--E-eff", type=float, default=274.0748756568)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--R", type=float, default=1.0)
    ap.add_argument("--a", type=float, default=None)
    ap.add_argument("--outdir", default="outputs_accessible_area_budget")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows, summary = evaluate(args.E_eff, args.L_K, args.R, args.a)
    write_csv(outdir/"accessible_area_budget_candidates.csv", rows)
    write_csv(outdir/"accessible_area_budget_summary.csv", [summary])

    theorem = [
        {
            "step": "accessible_radius",
            "formula": "R_acc = R-a",
            "status": "geometric definition of phase-accessible radial scale",
        },
        {
            "step": "accessible_area_fraction",
            "formula": "f_A = A_acc/A_out = (R-a)^2/R^2",
            "status": "derived from spherical screen area scaling",
        },
        {
            "step": "accessible_budget",
            "formula": "M_acc = M_total f_A",
            "status": "derived if phase budget is area-carried",
        },
        {
            "step": "half_budget_gate",
            "formula": "M_total = E_eff/2",
            "status": "open primitive-equation gate",
        },
        {
            "step": "interior_Hessian",
            "formula": "Lambda_phi = M_acc/(R-a)^2 = E_eff/(2 R^2); for R=1, E_eff/2",
            "status": "conditional on half_budget_gate",
        },
    ]
    write_csv(outdir/"accessible_area_budget_theorem_steps.csv", theorem)

    Eeff = args.E_eff
    target = Eeff/2.0
    a = summary["a"]
    R = summary["R"]
    Racc = summary["R_accessible"]

    report = f"""# Accessible-area phase-budget gate

## Derived geometry

\[
R_{{acc}}=R-a={Racc:.12g}.
\]

The accessible area fraction is

\[
f_A=\frac{{A_{{acc}}}}{{A_{{out}}}}
=\frac{{4\pi(R-a)^2}}{{4\pi R^2}}
=\left(\frac{{R-a}}{{R}}\right)^2
={summary['area_fraction']:.12g}.
\]

For \(R=1\),

\[
f_A=(R-a)^2.
\]

## Budget implication

If the total phase budget is independently

\[
M_{{total}}=\frac{{E_{{eff}}}}{{2}},
\]

and the budget is carried by accessible area, then

\[
M_{{acc}}=M_{{total}}f_A
=\frac{{E_{{eff}}}}{{2}}(R-a)^2.
\]

The previously derived optimal radial profile gives

\[
\Lambda_\phi=\frac{{M_{{acc}}}}{{(R-a)^2}}
=\frac{{E_{{eff}}}}{{2}}.
\]

## Numerical values

\[
E_{{eff}}/2={target:.12g},
\qquad
a={a:.12g},
\qquad
(R-a)^2={summary['area_fraction']:.12g}.
\]

Thus

\[
M_{{acc}}={summary['M_required']:.12g}.
\]

## Status

The accessible-area factor is derived.  The remaining primitive gate is

\[
M_{{total}}=\frac{{E_{{eff}}}}{{2}}.
\]

Therefore the interior phase-Hessian gate is reduced to an independent
half-budget theorem.
"""
    (outdir/"accessible_area_budget_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Accessible-area reduction of the phase-budget gate}
\label{app:accessible-area-phase-budget}

The radial phase-Hessian optimization gives
\[
  \Lambda_\phi=\frac{M}{(R-a)^2}
\]
for the optimal profile \(n_{\rm eff}(r)\propto r^{-2}\).  The remaining
budget condition is
\[
  M=\frac{E_{\rm eff}}{2}(R-a)^2.
\]
This factor has a geometric interpretation.  The phase-accessible radial scale
is
\[
  R_{\rm acc}=R-a,
\]
so the accessible spherical area fraction is
\[
  f_A
  =
  \frac{4\pi(R-a)^2}{4\pi R^2}
  =
  \left(\frac{R-a}{R}\right)^2.
\]
For the normalized cell \(R=1\),
\[
  f_A=(R-a)^2.
\]
Therefore, if the total interior phase budget is independently
\[
  M_{\rm total}=\frac{E_{\rm eff}}{2},
\]
and if this budget is carried by accessible area, then
\[
  M_{\rm acc}
  =
  M_{\rm total}f_A
  =
  \frac{E_{\rm eff}}{2}(R-a)^2.
\]
Substitution into the radial optimum gives
\[
  \Lambda_\phi
  =
  \frac{M_{\rm acc}}{(R-a)^2}
  =
  \frac{E_{\rm eff}}{2}.
\]
Thus the accessible-area factor is derived, but the primitive gate is reduced
to the half-budget identity \(M_{\rm total}=E_{\rm eff}/2\).
"""
    (outdir/"accessible_area_budget_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Accessible-area phase-budget gate")
    print("="*72)
    print(f"a                       : {a:.12g}")
    print(f"R-a                     : {Racc:.12g}")
    print(f"area fraction           : {summary['area_fraction']:.12g}")
    print(f"E_eff/2                 : {target:.12g}")
    print(f"M_acc required          : {summary['M_required']:.12g}")
    print("exact candidate          : half_budget_area_projected")
    print("status                   : ACCESSIBLE_AREA_FACTOR_DERIVED_HALF_BUDGET_OPEN")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
