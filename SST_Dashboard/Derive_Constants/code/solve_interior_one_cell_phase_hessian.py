#!/usr/bin/env python3
"""
solve_interior_one_cell_phase_hessian.py

Interior one-cell phase-Hessian solver for the remaining Hodge gate

    Lambda_phi = E_eff/2.

Purpose
-------
The exterior Hodge calculation already proves

    q_phi = 1,
    Lambda_phi = 4*pi*R*K_cell.

The remaining gate is an interior one-cell phase Hessian.  This script solves
the radial weighted phase problem

    div(n_eff(r) grad theta) = 0,

on a spherical shell a <= r <= R with

    theta(a)=0, theta(R)=phi.

For a radial density n_eff(r), the minimized phase energy is

    A(phi) = 1/2 Lambda_phi phi^2,

where

    Lambda_phi = 4*pi / integral_a^R [dr/(n_eff(r) r^2)].

The script compares Lambda_phi to E_eff/2 without using that target as input
unless the user explicitly asks for the required density normalization.

Epistemic status
----------------
This closes the interior Hessian gate only if n_eff(r) and its overall
normalization are supplied independently by the finite-cell/GP model.  If the
script is run in --solve-required-normalization mode, the result is a diagnostic
normalization requirement, not a derivation.

Usage
-----
    python solve_interior_one_cell_phase_hessian.py --outdir outputs_interior_phase

With E_eff comparison:
    python solve_interior_one_cell_phase_hessian.py --E-eff 274.0748756568 --inner-radius 0.0152703116982

Find required n0:
    python solve_interior_one_cell_phase_hessian.py --E-eff 274.0748756568 --solve-required-normalization
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
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def trapz(y, x):
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def density_profile(r: np.ndarray, mode: str, n0: float, a: float, R: float, xi: float, power: float):
    if mode == "constant":
        return n0*np.ones_like(r)
    if mode == "linear_ramp":
        t = (r-a)/max(R-a, 1e-30)
        return n0*np.clip(t, 0, 1)
    if mode == "gp_wall":
        # Smooth wall density rising from inner boundary.
        x = (r-a)/max(xi, 1e-30)
        return n0*np.tanh(x/np.sqrt(2.0))**2
    if mode == "power":
        return n0*(r/R)**power
    raise ValueError(mode)


def lambda_phase(a: float, R: float, mode: str, n0: float, xi: float, power: float, n_grid: int):
    r = np.linspace(a, R, n_grid)
    n = density_profile(r, mode, n0, a, R, xi, power)
    n = np.maximum(n, 1e-30)
    integrand = 1.0/(n*r*r)
    I = trapz(integrand, r)
    Lambda = 4.0*math.pi/I
    # normalized theta for phi=1:
    cumulative = np.zeros_like(r)
    # cumulative integral from a to r
    vals = integrand
    cumulative[1:] = np.cumsum(0.5*(vals[1:]+vals[:-1])*np.diff(r))
    theta = cumulative/I
    return Lambda, I, r, n, theta


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inner-radius", type=float, default=0.0152703116982)
    ap.add_argument("--outer-radius", type=float, default=1.0)
    ap.add_argument("--density-mode", choices=["constant", "linear_ramp", "gp_wall", "power"], default="constant")
    ap.add_argument("--n0", type=float, default=1.0)
    ap.add_argument("--xi", type=float, default=0.01)
    ap.add_argument("--power", type=float, default=0.0)
    ap.add_argument("--n-grid", type=int, default=10000)
    ap.add_argument("--E-eff", type=float, default=274.0748756568)
    ap.add_argument("--solve-required-normalization", action="store_true")
    ap.add_argument("--target-tol", type=float, default=1e-3)
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--outdir", default="outputs_interior_phase_hessian")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    Lambda, I, r, n, theta = lambda_phase(args.inner_radius, args.outer_radius, args.density_mode, args.n0, args.xi, args.power, args.n_grid)
    target = args.E_eff/2.0 if args.E_eff is not None else None
    ratio = Lambda/target if target else float("nan")

    # Required normalization: Lambda scales linearly with n0.
    Lambda_unit, I_unit, _, _, _ = lambda_phase(args.inner_radius, args.outer_radius, args.density_mode, 1.0, args.xi, args.power, args.n_grid)
    n0_required = target/Lambda_unit if target else float("nan")
    K_cell_from_Lambda = Lambda/(4.0*math.pi*args.outer_radius)
    K_target = args.E_eff/(8.0*math.pi*args.outer_radius)

    status = "PASS_INTERIOR_HESSIAN_TARGET" if abs(ratio-1.0) <= args.target_tol else "OPEN_INTERIOR_HESSIAN_GATE"
    if args.solve_required_normalization:
        status = "DIAGNOSTIC_REQUIRED_NORMALIZATION_NOT_DERIVATION"

    summary = [{
        "inner_radius": args.inner_radius,
        "outer_radius": args.outer_radius,
        "density_mode": args.density_mode,
        "n0": args.n0,
        "xi": args.xi,
        "power": args.power,
        "integral_I": I,
        "Lambda_phi": Lambda,
        "E_eff": args.E_eff,
        "target_Eeff_over_2": target,
        "Lambda_over_target": ratio,
        "n0_required_to_match_target": n0_required,
        "K_cell_from_Lambda": K_cell_from_Lambda,
        "K_target_Eeff_over_8piR": K_target,
        "status": status,
    }]
    write_csv(outdir/"interior_phase_hessian_summary.csv", summary)

    # Save profile sparsely.
    step = max(1, len(r)//1000)
    write_csv(outdir/"interior_phase_profile.csv", [
        {"r": float(rr), "n_eff": float(nn), "theta_phi1": float(tt)}
        for rr, nn, tt in zip(r[::step], n[::step], theta[::step])
    ])

    sens = []
    for mode in ["constant", "linear_ramp", "gp_wall", "power"]:
        for a in [args.inner_radius, 0.05, 0.1, 0.25, 0.5]:
            if a >= args.outer_radius:
                continue
            Lm, Im, *_ = lambda_phase(a, args.outer_radius, mode, 1.0, args.xi, args.power, args.n_grid)
            sens.append({
                "density_mode": mode,
                "inner_radius": a,
                "Lambda_for_n0_1": Lm,
                "n0_required_for_Eeff_over_2": target/Lm if target else float("nan"),
            })
    write_csv(outdir/"interior_phase_sensitivity.csv", sens)

    report = f"""# Interior one-cell phase Hessian

Problem:
\[
\nabla\cdot(n_{{eff}}(r)\nabla\theta)=0,\quad
\theta(a)=0,\quad \theta(R)=\phi.
\]

Analytic radial Hessian:
\[
\Lambda_\phi=\frac{{4\pi}}{{\int_a^R dr/[n_{{eff}}(r)r^2]}}.
\]

Parameters:
- a = {args.inner_radius}
- R = {args.outer_radius}
- density mode = {args.density_mode}
- n0 = {args.n0}

Result:
\[
\Lambda_\phi={Lambda:.12g}.
\]

Target:
\[
E_{{eff}}/2={target:.12g}.
\]

Ratio:
\[
\Lambda_\phi/(E_{{eff}}/2)={ratio:.12g}.
\]

Required n0 if used diagnostically:
\[
n0_{{required}}={n0_required:.12g}.
\]

Status: `{status}`.

If n0_required is solved from the target, this is not a derivation.  The gate
closes only when n_eff and n0 are supplied independently by the interior
finite-cell GP/Hodge model.
"""
    (outdir/"interior_phase_hessian_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Interior one-cell phase-Hessian target}
The exterior Hodge calculation gives
\[
  \Lambda_\phi=4\pi R K_{\rm cell}.
\]
The missing interior gate is
\[
  \Lambda_\phi=\frac{E_{\rm eff}}{2}.
\]
For a radial interior phase stiffness \(n_{\rm eff}(r)\), the phase field solves
\[
  \nabla\cdot(n_{\rm eff}(r)\nabla\theta)=0,
  \qquad
  \theta(a)=0,\quad \theta(R)=\phi.
\]
The minimized action is
\[
  \mathcal A_\phi^{\rm int}
  =
  \frac12\Lambda_\phi\phi^2,
\]
with
\[
  \Lambda_\phi
  =
  \frac{4\pi}
       {\displaystyle\int_a^R\frac{dr}{n_{\rm eff}(r)r^2}}.
\]
This closes the gate only if \(n_{\rm eff}(r)\) and its normalization are
derived independently.  Solving for the normalization required to match
\(E_{\rm eff}/2\) is a diagnostic, not a derivation.
"""
    (outdir/"interior_phase_hessian_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(7.2,4.5))
            ax.plot(r, theta, label=r"$\theta(r)/\phi$")
            ax2 = ax.twinx()
            ax2.plot(r, n, linestyle="--", label=r"$n_{\rm eff}(r)$")
            ax.set_xlabel("r")
            ax.set_ylabel(r"$\theta/\phi$")
            ax2.set_ylabel(r"$n_{\rm eff}$")
            ax.set_title("Interior phase Hessian radial solution")
            fig.tight_layout()
            fig.savefig(outdir/"interior_phase_profile.png", dpi=180)
            plt.close(fig)
        except Exception:
            pass

    print("Interior one-cell phase Hessian")
    print("="*72)
    print(f"Lambda_phi        : {Lambda:.12g}")
    print(f"E_eff/2 target    : {target:.12g}")
    print(f"ratio             : {ratio:.12g}")
    print(f"n0 required       : {n0_required:.12g}")
    print(f"K_cell            : {K_cell_from_Lambda:.12g}")
    print(f"status            : {status}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
