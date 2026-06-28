#!/usr/bin/env python3
"""
derive_phase_hessian_density_budget.py

Independent density-budget audit for the interior phase-Hessian gate

    Lambda_phi = E_eff/2.

The radial phase Hessian is

    Lambda_phi = 4*pi / integral_a^R [dr/(n_eff(r) r^2)].

This script does not solve for n_eff by matching Lambda_phi unless explicitly
requested.  Instead, it assigns a total stiffness budget

    M = integral 4*pi r^2 n_eff(r) dr

from independent candidate budgets, normalizes density shapes to that budget,
and computes Lambda_phi.  The variationally optimal radial density for maximum
phase stiffness at fixed budget is also included:

    n_eff(r) proportional to 1/r^2.

For this optimal profile,

    Lambda_phi = M/(R-a)^2.

Thus the script exposes exactly what independent density budget would be needed
for Lambda_phi=E_eff/2.

Epistemic status:
    - A match with a pre-declared independent budget supports the gate.
    - Solving for the required budget is diagnostic, not a derivation.

Usage:
    python derive_phase_hessian_density_budget.py --outdir outputs_phase_budget
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List

import numpy as np


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def trapz(y, x):
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def shape_profile(r: np.ndarray, mode: str, a: float, R: float, xi: float, power: float) -> np.ndarray:
    if mode == "constant":
        g = np.ones_like(r)
    elif mode == "optimal_inverse_r2":
        g = 1.0/(r*r)
    elif mode == "gp_wall":
        x = (r-a)/max(xi, 1e-30)
        g = np.tanh(x/math.sqrt(2.0))**2
    elif mode == "core_shell":
        g = np.exp(-((r-a)/max(xi, 1e-30))**2)
    elif mode == "power":
        g = (r/R)**power
    else:
        raise ValueError(mode)
    return np.maximum(g, 1e-30)


def normalize_density_to_budget(r, g, M):
    norm = 4.0*math.pi*trapz(r*r*g, r)
    return (M/norm)*g, norm


def lambda_from_density(r, n):
    I = trapz(1.0/(np.maximum(n, 1e-30)*r*r), r)
    return 4.0*math.pi/I, I


def compute_case(a, R, mode, M, xi, power, n_grid):
    r = np.linspace(a, R, n_grid)
    g = shape_profile(r, mode, a, R, xi, power)
    n, raw_norm = normalize_density_to_budget(r, g, M)
    Lam, I = lambda_from_density(r, n)
    return {
        "mode": mode,
        "budget_M": M,
        "raw_shape_norm": raw_norm,
        "Lambda_phi": Lam,
        "integral_I": I,
        "n_min": float(np.min(n)),
        "n_max": float(np.max(n)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner-radius", type=float, default=0.0152703116982)
    parser.add_argument("--outer-radius", type=float, default=1.0)
    parser.add_argument("--E-eff", type=float, default=274.0748756568)
    parser.add_argument("--L-K", type=float, default=16.371637)
    parser.add_argument("--xi", type=float, default=0.03)
    parser.add_argument("--power", type=float, default=0.0)
    parser.add_argument("--n-grid", type=int, default=5000)
    parser.add_argument("--target-tol", type=float, default=1e-3)
    parser.add_argument("--outdir", default="outputs_phase_hessian_density_budget")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    a, R, Eeff = args.inner_radius, args.outer_radius, args.E_eff
    target = Eeff/2.0
    budgets = {
        "M_Eeff": Eeff,
        "M_Eeff_over_2": Eeff/2.0,
        "M_leading_inverse_alpha": (8.0*math.pi/3.0)*args.L_K,
        "M_LK_squared": args.L_K*args.L_K,
        "M_unit": 1.0,
    }
    modes = ["constant", "optimal_inverse_r2", "gp_wall", "core_shell", "power"]

    rows = []
    for bname, M in budgets.items():
        for mode in modes:
            c = compute_case(a, R, mode, M, args.xi, args.power, args.n_grid)
            c["budget_name"] = bname
            c["target_Eeff_over_2"] = target
            c["ratio_to_target"] = c["Lambda_phi"]/target
            c["abs_rel_error_to_target"] = abs(c["Lambda_phi"]/target - 1.0)
            c["status"] = "PASS_PREDECLARED_BUDGET_MATCH" if c["abs_rel_error_to_target"] <= args.target_tol else "NO_MATCH"
            rows.append(c)
    write_csv(outdir/"phase_density_budget_table.csv", rows)

    # Required budgets by profile shape.
    req_rows = []
    for mode in modes:
        unit = compute_case(a, R, mode, 1.0, args.xi, args.power, args.n_grid)
        M_req = target/unit["Lambda_phi"]
        req_rows.append({
            "mode": mode,
            "Lambda_for_M1": unit["Lambda_phi"],
            "M_required_for_target": M_req,
            "M_required_over_Eeff": M_req/Eeff,
            "M_required_over_Eeff_over_2": M_req/(Eeff/2.0),
        })
    write_csv(outdir/"phase_density_required_budget.csv", req_rows)

    # Choose best predeclared case.
    best = min(rows, key=lambda x: x["abs_rel_error_to_target"])
    summary = [{
        "inner_radius": a,
        "outer_radius": R,
        "E_eff": Eeff,
        "target_Eeff_over_2": target,
        "best_budget_name": best["budget_name"],
        "best_mode": best["mode"],
        "best_Lambda_phi": best["Lambda_phi"],
        "best_ratio_to_target": best["ratio_to_target"],
        "best_status": best["status"],
        "optimal_profile_formula": "n_eff proportional to 1/r^2 gives Lambda=M/(R-a)^2",
        "M_required_optimal_inverse_r2": [r for r in req_rows if r["mode"]=="optimal_inverse_r2"][0]["M_required_for_target"],
        "status": "INTERIOR_PHASE_GATE_CLOSED_BY_PREDECLARED_BUDGET" if best["status"].startswith("PASS") else "OPEN_DENSITY_BUDGET_GATE",
    }]
    write_csv(outdir/"phase_density_budget_summary.csv", summary)

    report = f"""# Phase-Hessian density-budget audit

Target:
\[
\Lambda_\phi=E_{{eff}}/2={target:.12g}.
\]

Best predeclared case:
- budget = `{best['budget_name']}`
- density mode = `{best['mode']}`
- Lambda = `{best['Lambda_phi']:.12g}`
- ratio = `{best['ratio_to_target']:.12g}`

Status: `{summary[0]['status']}`.

For the variationally optimal radial profile \(n(r)\propto1/r^2\),
\[
\Lambda_\phi=\frac{{M}}{{(R-a)^2}}.
\]
The required budget for the target is
\[
M_{{req}}={summary[0]['M_required_optimal_inverse_r2']:.12g}.
\]

If this budget is chosen by matching the target, it is not a derivation.  The
gate closes only if the same budget and density shape follow independently
from the finite-cell GP/Hodge model.
"""
    (outdir/"phase_density_budget_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Density-budget form of the interior phase-Hessian gate}
For radial phase stiffness \(n_{\rm eff}(r)\),
\[
  \Lambda_\phi
  =
  \frac{4\pi}
       {\displaystyle\int_a^R\frac{dr}{n_{\rm eff}(r)r^2}}.
\]
If the total stiffness budget
\[
  M=\int_a^R4\pi r^2 n_{\rm eff}(r)\,dr
\]
is fixed independently, the variational profile that maximizes
\(\Lambda_\phi\) is
\[
  n_{\rm eff}(r)\propto \frac1{r^2},
\]
for which
\[
  \Lambda_\phi=\frac{M}{(R-a)^2}.
\]
Thus the remaining gate may be recast as an independent density-budget problem:
derive \(M\) and the \(1/r^2\)-type radial distribution from the interior
finite-cell dynamics.  Solving for \(M\) from \(\Lambda_\phi=E_{\rm eff}/2\) is
only diagnostic.
"""
    (outdir/"phase_density_budget_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Phase-Hessian density-budget audit")
    print("="*72)
    print(f"target Lambda       : {target:.12g}")
    print(f"best budget         : {best['budget_name']}")
    print(f"best mode           : {best['mode']}")
    print(f"best Lambda         : {best['Lambda_phi']:.12g}")
    print(f"best ratio          : {best['ratio_to_target']:.12g}")
    print(f"M_required optimal  : {summary[0]['M_required_optimal_inverse_r2']:.12g}")
    print(f"status              : {summary[0]['status']}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
