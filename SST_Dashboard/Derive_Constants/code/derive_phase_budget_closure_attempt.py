#!/usr/bin/env python3
"""
derive_phase_budget_closure_attempt.py

Attempt to close the remaining interior phase-Hessian gate

    Lambda_phi = E_eff/2

without inserting Lambda_phi directly.

What is derived here
--------------------
For a radial shell a <= r <= R with phase stiffness n(r),

    Lambda_phi = 4*pi / integral_a^R dr/[n(r) r^2].

Given an independently fixed total radial phase budget

    M = integral_a^R 4*pi r^2 n(r) dr,

the variational optimum is

    n_*(r) = M/[4*pi*(R-a)] * 1/r^2,

and

    Lambda_max = M/(R-a)^2.

This part is a theorem from a one-line Euler-Lagrange/Cauchy-Schwarz argument.

What remains open
-----------------
The target Lambda_phi=E_eff/2 is obtained iff

    M = (E_eff/2) (R-a)^2.

This script tests whether common independent budget candidates give that value.
If a candidate is chosen because it equals the required budget, that is a
closure, not a derivation.

Usage
-----
    python derive_phase_budget_closure_attempt.py --outdir outputs_phase_budget_closure

The default uses:
    L_K = 16.371637,
    a = eta_K = 1/(4 L_K),
    R = 1,
    E_eff = 274.0748756568.
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


def budget_candidates(Eeff: float, a: float, R: float, L: float) -> List[Dict]:
    T = Eeff/2.0
    ell = R - a
    candidates = [
        ("M_unit", 1.0, "unit budget"),
        ("M_LK", L, "ropelength budget"),
        ("M_8piL_over_3", 8.0*math.pi*L/3.0, "leading inverse-alpha ropelength scale"),
        ("M_Eeff_over_2", T, "raw half effective scale"),
        ("M_Eeff_over_2_times_accessible_length", T*ell, "linear accessible-length budget"),
        ("M_Eeff_over_2_times_accessible_area", T*ell*ell, "area / squared-accessible-length budget"),
        ("M_Eeff_over_2_times_accessible_volume", T*(R**3-a**3)/(R**3), "volume fraction budget"),
        ("M_required", T*ell*ell, "required by Lambda=Eeff/2 for optimal 1/r^2 profile"),
    ]
    rows = []
    for name, M, interpretation in candidates:
        Lambda = M/(ell*ell)
        rows.append({
            "candidate": name,
            "M": M,
            "interpretation": interpretation,
            "Lambda_optimal": Lambda,
            "target_Eeff_over_2": T,
            "ratio_to_target": Lambda/T,
            "relative_error": Lambda/T - 1.0,
            "exact_match": abs(Lambda/T - 1.0) < 1e-12,
            "epistemic_status": "diagnostic_required_value" if name=="M_required" else ("candidate_exact_if_accessible_area_budget_is_derived" if name=="M_Eeff_over_2_times_accessible_area" else "tested_candidate"),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--E-eff", type=float, default=274.0748756568)
    ap.add_argument("--inner-radius", type=float, default=None)
    ap.add_argument("--outer-radius", type=float, default=1.0)
    ap.add_argument("--outdir", default="outputs_phase_budget_closure")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    a = 1.0/(4.0*args.L_K) if args.inner_radius is None else args.inner_radius
    R = args.outer_radius
    ell = R-a
    T = args.E_eff/2.0
    M_required = T*ell*ell

    rows = budget_candidates(args.E_eff, a, R, args.L_K)
    write_csv(outdir/"phase_budget_candidate_table.csv", rows)

    theorem_rows = [
        {
            "claim": "radial phase Hessian",
            "formula": "Lambda_phi = 4*pi / int_a^R dr/[n(r) r^2]",
            "status": "derived by radial Euler-Lagrange equation",
        },
        {
            "claim": "optimal density for fixed budget M",
            "formula": "n_*(r) = M/[4*pi*(R-a)] * 1/r^2",
            "status": "derived by variational optimization / Cauchy-Schwarz",
        },
        {
            "claim": "maximal Hessian at fixed budget",
            "formula": "Lambda_max = M/(R-a)^2",
            "status": "derived",
        },
        {
            "claim": "required budget for Lambda=E_eff/2",
            "formula": "M_required = (E_eff/2)(R-a)^2",
            "status": "diagnostic unless independently derived",
        },
    ]
    write_csv(outdir/"phase_budget_theorem_steps.csv", theorem_rows)

    best = min(rows, key=lambda r: abs(r["relative_error"]))
    summary = [{
        "L_K": args.L_K,
        "E_eff": args.E_eff,
        "target_Eeff_over_2": T,
        "inner_radius_a": a,
        "outer_radius_R": R,
        "accessible_length_R_minus_a": ell,
        "accessible_squared_factor": ell*ell,
        "M_required": M_required,
        "M_required_over_Eeff_over_2": M_required/T,
        "best_candidate": best["candidate"],
        "best_ratio_to_target": best["ratio_to_target"],
        "best_relative_error": best["relative_error"],
        "gate_status": "REDUCED_TO_ACCESSIBLE_AREA_BUDGET_GATE",
    }]
    write_csv(outdir/"phase_budget_closure_summary.csv", summary)

    report = f"""# Phase-budget closure attempt

## Derived theorem

For fixed radial phase budget

\\[
M=\\int_a^R4\\pi r^2 n(r)\\,dr,
\\]

the density that maximizes the interior phase Hessian is

\\[
n_*(r)=\\frac{{M}}{{4\\pi(R-a)}}\\frac1{{r^2}},
\\]

and

\\[
\\Lambda_{{\\max}}=\\frac{{M}}{{(R-a)^2}}.
\\]

## Numerical values

\\[
a=\\eta_K={a:.12g},\\qquad R=1,
\\qquad R-a={ell:.12g}.
\\]

\\[
E_{{eff}}/2={T:.12g}.
\\]

The required budget is

\\[
M_{{req}}=\\frac{{E_{{eff}}}}{{2}}(R-a)^2={M_required:.12g}.
\\]

Thus

\\[
\\frac{{M_{{req}}}}{{E_{{eff}}/2}}=(R-a)^2={ell*ell:.12g}.
\\]

## Status

The shape \(n(r)\\propto1/r^2\) is derived.  The remaining gate is no longer the
radial profile but the independent derivation of the accessible-area budget

\\[
M=\\frac{{E_{{eff}}}}{{2}}(R-a)^2.
\\]

If this budget is postulated because it matches the target, it is a closure.
If it follows independently from the finite-cell phase-stiffness budget, then
the interior Hessian gate closes.
"""
    (outdir/"phase_budget_closure_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Reduction of the interior phase-Hessian gate to an accessible-area budget}
For radial stiffness \(n(r)\) on \(a\le r\le R\), the minimized phase Hessian is
\[
  \Lambda_\phi
  =
  \frac{4\pi}
       {\displaystyle\int_a^R\frac{dr}{n(r)r^2}}.
\]
Fix the total radial phase-stiffness budget
\[
  M=\int_a^R4\pi r^2 n(r)\,dr.
\]
Variation with a Lagrange multiplier gives
\[
  n_*(r)
  =
  \frac{M}{4\pi(R-a)}\,\frac{1}{r^2}.
\]
Equivalently, the same result follows from the Cauchy--Schwarz inequality.
For this optimal profile,
\[
  \Lambda_{\max}
  =
  \frac{M}{(R-a)^2}.
\]
Therefore the desired interior relation
\[
  \Lambda_\phi=\frac{E_{\rm eff}}{2}
\]
is equivalent, in the optimized radial phase channel, to
\[
  M
  =
  \frac{E_{\rm eff}}{2}(R-a)^2.
\]
For the trefoil pressure cell,
\[
  a=\eta_K=\frac{1}{4\mathcal L_K}=1.52703116982\times10^{-2},
\]
so the required budget is
\[
  M_{\rm req}
  =
  \frac{E_{\rm eff}}{2}(1-\eta_K)^2.
\]
This does not yet close the gate: the profile \(n(r)\propto r^{-2}\) is derived,
but the accessible-area budget \(M_{\rm req}\) must still be obtained from the
interior finite-cell dynamics rather than imposed by matching
\(\Lambda_\phi=E_{\rm eff}/2\).
"""
    (outdir/"phase_budget_closure_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Phase-budget closure attempt")
    print("="*72)
    print(f"a=eta_K              : {a:.12g}")
    print(f"R-a                  : {ell:.12g}")
    print(f"(R-a)^2              : {ell*ell:.12g}")
    print(f"E_eff/2 target       : {T:.12g}")
    print(f"M_required           : {M_required:.12g}")
    print(f"best candidate       : {best['candidate']}")
    print(f"best ratio           : {best['ratio_to_target']:.12g}")
    print("status               : REDUCED_TO_ACCESSIBLE_AREA_BUDGET_GATE")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
