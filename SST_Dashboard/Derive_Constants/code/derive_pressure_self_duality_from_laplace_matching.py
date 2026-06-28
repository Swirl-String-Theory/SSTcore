#!/usr/bin/env python3
"""
derive_pressure_self_duality_from_laplace_matching.py

Laplace-pressure / matched-asymptotic audit for the finite-cell radius action

    A_chi = chi_R + N_p/chi_R.

Purpose
-------
The previous symbolic script proved the self-dual reciprocal action if equal
inner/outer pressure normalization was assumed.  This script makes the next
step explicit: it tests whether the equal normalization is supported by the
SST pressure identity

    P_Laplace = F_swirl/(2*pi*r_c^2)
              ≈ (1/2) rho_core |v_swirl|^2 = P_kinetic.

If this identity holds, the inner core pressure modulus and outer cell pressure
modulus can be assigned the same leading coefficient.  Then the leading
scale-homogeneous matched action is

    A_chi = chi_R + N_p/chi_R,

and stationarity gives

    chi_R = sqrt(N_p).

For N_p=4,

    chi_R = 2,
    lambda_chi = 4.

Epistemic status
----------------
This script can support the claim:

    A_chi is derived within the Laplace-matched reciprocal pressure model.

It does not prove that the full primitive equations contain no same-order
nonreciprocal terms, e.g. c log chi_R, d chi_R^2, or e/chi_R^2.  It reports
those as explicit robustness gates.

Usage
-----
    python derive_pressure_self_duality_from_laplace_matching.py --outdir outputs_laplace_self_duality

Sensitivity:
    python derive_pressure_self_duality_from_laplace_matching.py --pressure-ratio 1.05
    python derive_pressure_self_duality_from_laplace_matching.py --N-p 9
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List

import numpy as np


SST_DEFAULTS = {
    "v_swirl": 1.09384563e6,                  # m/s
    "r_c": 1.40897017e-15,                   # m
    "rho_core": 3.8934358266918687e18,       # kg/m^3
    "F_swirl_max": 29.053507,                # N
}


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def pressure_identity(v_swirl: float, r_c: float, rho_core: float, F_swirl: float) -> Dict[str, float]:
    P_kin = 0.5 * rho_core * v_swirl * v_swirl
    # The 2*pi denominator is the natural circular core-area normalization:
    # force per circumference-normalized disk area.
    P_laplace = F_swirl / (2.0 * math.pi * r_c * r_c)
    ratio = P_laplace / P_kin
    return {
        "P_kinetic_Pa": P_kin,
        "P_laplace_Pa": P_laplace,
        "pressure_ratio_laplace_over_kinetic": ratio,
        "relative_mismatch": ratio - 1.0,
    }


def action_stationary(Np: float, pressure_ratio: float) -> Dict[str, float]:
    # General matched action normalized by outer coefficient:
    # A = chi + mu Np/chi, mu = P_inner/P_outer.
    mu = pressure_ratio
    chi_star = math.sqrt(mu * Np)
    lambda_chi = mu * Np
    A_star = chi_star + mu * Np / chi_star
    second_derivative = 2.0 * mu * Np / (chi_star ** 3)
    return {
        "mu_inner_over_outer": mu,
        "N_p": Np,
        "lambda_chi": lambda_chi,
        "chi_R_star": chi_star,
        "A_chi_star": A_star,
        "second_derivative_at_star": second_derivative,
    }


def duality_residual(chi_grid: np.ndarray, Np: float, mu: float) -> Dict[str, float]:
    # Minimal action A_mu=chi+mu Np/chi. Self-duality under D: chi -> Np/chi
    # is exact only when mu=1:
    # A_mu(D chi)-A_mu(chi) = (mu-1)(chi - Np/chi).
    A = chi_grid + mu * Np / chi_grid
    D = Np / chi_grid
    A_dual = D + mu * Np / D
    residual = A_dual - A
    return {
        "duality_residual_max_abs": float(np.max(np.abs(residual))),
        "duality_residual_rms": float(np.sqrt(np.mean(residual * residual))),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--N-p", type=float, default=4.0, help="Pressure sector count.")
    ap.add_argument("--pressure-ratio", type=float, default=None, help="Override mu=P_inner/P_outer. If omitted, use SST pressure identity.")
    ap.add_argument("--v-swirl", type=float, default=SST_DEFAULTS["v_swirl"])
    ap.add_argument("--r-c", type=float, default=SST_DEFAULTS["r_c"])
    ap.add_argument("--rho-core", type=float, default=SST_DEFAULTS["rho_core"])
    ap.add_argument("--F-swirl", type=float, default=SST_DEFAULTS["F_swirl_max"])
    ap.add_argument("--chi-min", type=float, default=0.5)
    ap.add_argument("--chi-max", type=float, default=8.0)
    ap.add_argument("--chi-n", type=int, default=2000)
    ap.add_argument("--tol-pressure-match", type=float, default=5e-6)
    ap.add_argument("--outdir", default="outputs_laplace_self_duality")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    pid = pressure_identity(args.v_swirl, args.r_c, args.rho_core, args.F_swirl)
    mu = args.pressure_ratio if args.pressure_ratio is not None else pid["pressure_ratio_laplace_over_kinetic"]

    stat = action_stationary(args.N_p, mu)
    chi = np.linspace(args.chi_min, args.chi_max, args.chi_n)
    dual = duality_residual(chi, args.N_p, mu)

    # Self-dual ideal using mu=1.
    stat_selfdual = action_stationary(args.N_p, 1.0)
    dual_selfdual = duality_residual(chi, args.N_p, 1.0)

    pressure_match = abs(pid["relative_mismatch"]) <= args.tol_pressure_match
    chi_matches_2 = abs(stat["chi_R_star"] - 2.0) <= 1e-5 if abs(args.N_p - 4.0) < 1e-12 else False
    selfdual_exact = abs(mu - 1.0) <= args.tol_pressure_match

    rows = [
        {
            "gate": "SST_pressure_identity",
            "claim": "F_swirl/(2*pi*r_c^2) equals 1/2 rho_core v_swirl^2",
            "value": pid["pressure_ratio_laplace_over_kinetic"],
            "status": "MATCHED" if pressure_match else "MISMATCHED",
            "notes": f"relative mismatch={pid['relative_mismatch']:.6e}; tolerance={args.tol_pressure_match}",
        },
        {
            "gate": "inner_outer_equal_normalization",
            "claim": "mu=P_inner/P_outer=1",
            "value": mu,
            "status": "SUPPORTED_BY_PRESSURE_IDENTITY" if selfdual_exact else "SENSITIVITY_VARIANT",
            "notes": "mu may be overridden to test robustness.",
        },
        {
            "gate": "self_dual_action",
            "claim": "A_chi=chi_R+N_p/chi_R",
            "value": "A=chi+mu*Np/chi",
            "status": "DERIVED_IN_LAPLACE_MATCHED_RECIPROCAL_MODEL" if selfdual_exact else "GENERALIZED_ACTION_WITH_MU",
            "notes": "Exact duality chi<->Np/chi requires mu=1.",
        },
        {
            "gate": "radius_stationarity",
            "claim": "chi_R=sqrt(mu*N_p)",
            "value": stat["chi_R_star"],
            "status": "CHI_R_2_FOR_NP_4" if chi_matches_2 else "SHIFTED_OR_NON_NP4",
            "notes": f"lambda_chi={stat['lambda_chi']}",
        },
        {
            "gate": "higher_order_terms",
            "claim": "no same-order log/quadratic terms",
            "value": "not tested by pressure identity",
            "status": "OPEN_PRIMITIVE_EQUATION_GATE",
            "notes": "Must be excluded by full matched asymptotics or shown subleading.",
        },
    ]
    write_csv(outdir / "laplace_self_duality_gates.csv", rows)

    summary = [{**pid, **stat, **dual,
                "N_p": args.N_p,
                "pressure_ratio_used": mu,
                "pressure_match_within_tolerance": pressure_match,
                "selfdual_exact_within_tolerance": selfdual_exact,
                "chi_matches_2_for_Np4": chi_matches_2,
                "selfdual_chi_R_star_for_mu1": stat_selfdual["chi_R_star"],
                "selfdual_lambda_chi_for_mu1": stat_selfdual["lambda_chi"],
                "selfdual_duality_residual_max_abs": dual_selfdual["duality_residual_max_abs"]}]
    write_csv(outdir / "laplace_self_duality_summary.csv", summary)

    sens = []
    for mm in [0.8, 0.95, 1.0, 1.05, 1.2, mu]:
        st = action_stationary(args.N_p, mm)
        du = duality_residual(chi, args.N_p, mm)
        sens.append({
            "mu": mm,
            "N_p": args.N_p,
            "lambda_chi": st["lambda_chi"],
            "chi_R_star": st["chi_R_star"],
            "A_chi_star": st["A_chi_star"],
            "duality_residual_rms": du["duality_residual_rms"],
        })
    write_csv(outdir / "laplace_self_duality_sensitivity.csv", sens)

    # Save chi curve for plotting.
    curve_rows = []
    for xx in chi:
        A_mu = xx + mu * args.N_p / xx
        A_self = xx + args.N_p / xx
        curve_rows.append({
            "chi_R": xx,
            "A_chi_mu": A_mu,
            "A_chi_selfdual": A_self,
            "A_dual_minus_A_mu": (args.N_p/xx + mu*xx) - A_mu,
        })
    write_csv(outdir / "laplace_self_duality_curve.csv", curve_rows)

    report = f"""# Laplace-matched pressure self-duality audit

## SST pressure identity

\\[
P_{{\\rm kin}}=\\frac12\\rho_{{\\rm core}}\\lVert\\mathbf v_{{\\circlearrowleft}}\\rVert^2
= {pid['P_kinetic_Pa']:.12e}\\,\\mathrm{{Pa}}.
\\]

\\[
P_{{\\rm Laplace}}=\\frac{{F_{{\\rm swirl}}^{{\\max}}}}{{2\\pi r_c^2}}
= {pid['P_laplace_Pa']:.12e}\\,\\mathrm{{Pa}}.
\\]

Ratio:

\\[
\\mu=P_{{\\rm Laplace}}/P_{{\\rm kin}}
= {pid['pressure_ratio_laplace_over_kinetic']:.12g}.
\\]

## Radius action

The matched reciprocal action is

\\[
A_\\chi=\\chi_R+\\mu\\frac{{N_p}}{{\\chi_R}}.
\\]

Stationarity gives

\\[
\\chi_R=\\sqrt{{\\mu N_p}}={stat['chi_R_star']:.12g}.
\\]

For \(N_p=4\) and \(\mu=1\), this gives

\\[
\\chi_R=2,\\qquad \\lambda_\\chi=4.
\\]

## Status

- Pressure match within tolerance: `{pressure_match}`.
- Self-duality exact within tolerance: `{selfdual_exact}`.
- Higher-order primitive-equation terms remain an open gate.
"""
    (outdir / "laplace_self_duality_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Laplace-matched pressure self-duality}
The core kinetic pressure and circular Laplace pressure are
\[
  P_{\rm kin}=\frac12\rho_{\rm core}
  \lVert\mathbf v_{\!\boldsymbol{\circlearrowleft}}\rVert^2,
  \qquad
  P_{\rm Laplace}=\frac{F_{\rm swirl}^{\max}}{2\pi r_c^2}.
\]
If these agree, the inner and outer pressure moduli are equal at leading order.
The reciprocal matched action is then
\[
  A_\chi(\chi_R)=\chi_R+\frac{N_p}{\chi_R}.
\]
More generally,
\[
  A_\chi(\chi_R)=\chi_R+\mu\frac{N_p}{\chi_R},
  \qquad
  \mu=\frac{P_{\rm in}}{P_{\rm out}}.
\]
Stationarity gives
\[
  \chi_R=\sqrt{\mu N_p}.
\]
Thus for \(N_p=4\) and \(\mu=1\),
\[
  \chi_R=2,\qquad \lambda_\chi=4.
\]
This derives the self-dual radius action within the Laplace-matched reciprocal
pressure model.  A full primitive-equation derivation must still exclude
same-order nonreciprocal terms such as \(\log\chi_R\), \(\chi_R^2\), or
\(\chi_R^{-2}\), or show that they are higher-order corrections.
"""
    (outdir / "laplace_self_duality_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.plot(chi, [r["A_chi_mu"] for r in curve_rows], label=f"mu={mu:.6g}")
        ax.plot(chi, [r["A_chi_selfdual"] for r in curve_rows], linestyle="--", label="mu=1")
        ax.axvline(stat["chi_R_star"], linestyle=":", label="stationary")
        ax.set_xlabel("chi_R")
        ax.set_ylabel("A_chi")
        ax.set_title("Matched reciprocal pressure action")
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / "laplace_self_duality_action.png", dpi=180)
        plt.close(fig)
    except Exception:
        pass

    print("Laplace-matched pressure self-duality audit")
    print("=" * 72)
    print(f"P_kinetic [Pa]    : {pid['P_kinetic_Pa']:.12e}")
    print(f"P_laplace [Pa]   : {pid['P_laplace_Pa']:.12e}")
    print(f"ratio mu         : {mu:.12g}")
    print(f"relative mismatch: {pid['relative_mismatch']:.6e}")
    print(f"N_p              : {args.N_p}")
    print(f"lambda_chi       : {stat['lambda_chi']:.12g}")
    print(f"chi_R_star       : {stat['chi_R_star']:.12g}")
    print(f"status           : {'DERIVED_IN_LAPLACE_MATCHED_RECIPROCAL_MODEL' if selfdual_exact else 'SENSITIVITY_VARIANT'}")
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
