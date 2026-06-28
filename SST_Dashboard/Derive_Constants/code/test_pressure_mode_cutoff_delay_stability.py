#!/usr/bin/env python3
"""
test_pressure_mode_cutoff_delay_stability.py

Delay/stability audit for the pressure-mode cutoff N_p=4.

Purpose
-------
The static SO(3) argument says that volume + centre-displacement pressure
constraints live in H_0 ⊕ H_1, giving N_p=1+3=4.  A reviewer may still ask:
why are l>=2 shape modes excluded dynamically?

This script tests a simple delay-feedback stability model for spherical
pressure modes:

    d a_l/dt = -nu_l a_l(t) + kappa_l a_l(t-tau),

with

    nu_l = nu0 + D l(l+1) + Q [l(l+1)]^2,
    kappa_l = kappa0 / (1 + [l(l+1)/ell_c]^p).

The characteristic roots are

    lambda_k = -nu_l + (1/tau) W_k(tau kappa_l exp(nu_l tau)),

where W_k is the Lambert W branch.  The script computes the maximum real root
per l.  A mode is classified as retained if it is constrained (l=0,1) and not
strongly damped, and suppressed if l>=2 has negative growth below a threshold.

Epistemic status
----------------
This is a stability-gate auditor, not a proof that nature must choose the
default parameters.  A successful run means "N_p=4 is dynamically consistent
inside the stated delay-stability model."  A robust derived claim requires a
parameter-free derivation of tau, kappa0, D, Q, and ell_c from the primitive
SST delay loop.

Usage
-----
    python test_pressure_mode_cutoff_delay_stability.py --outdir outputs_delay_mode_cutoff

Scan:
    python test_pressure_mode_cutoff_delay_stability.py --scan --outdir outputs_delay_mode_cutoff_scan
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from scipy.special import lambertw
    SCIPY_AVAILABLE = True
except Exception:
    lambertw = None
    SCIPY_AVAILABLE = False


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def mode_params(l: int, nu0: float, D: float, Q: float, kappa0: float, ell_c: float, p: float) -> Tuple[float, float]:
    L = l * (l + 1)
    nu_l = nu0 + D * L + Q * L * L
    kappa_l = kappa0 / (1.0 + (L / max(ell_c, 1e-12)) ** p)
    return nu_l, kappa_l


def max_real_root(nu: float, kappa: float, tau: float, branches: int) -> Tuple[float, int]:
    if not SCIPY_AVAILABLE:
        # Conservative approximation for small roots by fixed-point iteration on real axis.
        lam = -nu + kappa
        for _ in range(200):
            lam_new = -nu + kappa * math.exp(-lam * tau)
            if abs(lam_new - lam) < 1e-12:
                break
            lam = lam_new
        return float(lam), 0

    z = tau * kappa * math.exp(nu * tau)
    best = -1e300
    best_branch = 0
    for b in range(-branches, branches + 1):
        val = -nu + lambertw(z, b) / tau
        real = float(np.real(val))
        if real > best:
            best = real
            best_branch = b
    return best, best_branch


def evaluate(params: argparse.Namespace) -> Tuple[List[Dict], Dict]:
    rows = []
    retained = []
    suppressed = []
    for l in range(params.lmax + 1):
        nu_l, kappa_l = mode_params(l, params.nu0, params.D, params.Q, params.kappa0, params.ell_c, params.p)
        growth, branch = max_real_root(nu_l, kappa_l, params.tau, params.branches)
        constrained = l <= 1
        is_retained = constrained and growth >= -params.retention_margin
        is_suppressed = (l >= 2) and growth <= -params.suppression_margin
        classification = "retained_constraint_mode" if is_retained else ("suppressed_shape_mode" if is_suppressed else "ambiguous_or_unstable")
        if is_retained:
            retained.append(l)
        if is_suppressed:
            suppressed.append(l)
        rows.append({
            "ell": l,
            "degeneracy": 2*l + 1,
            "L_laplacian": l*(l+1),
            "nu_l": nu_l,
            "kappa_l": kappa_l,
            "tau": params.tau,
            "max_real_root": growth,
            "best_branch": branch,
            "constrained_by_pressure_moments": constrained,
            "classification": classification,
        })
    pass_gate = set(retained) == {0, 1} and all(l in suppressed for l in range(2, params.lmax + 1))
    summary = {
        "retained_modes": str(retained),
        "suppressed_modes": str(suppressed),
        "pass_Np4_cutoff_gate": pass_gate,
        "N_p_from_retained_constraints": sum(2*l+1 for l in retained if l <= 1),
        "status": "DYNAMICALLY_CONSISTENT_WITH_NP4" if pass_gate else "NOT_A_CLEAN_NP4_CUTOFF",
    }
    return rows, summary


def scan_parameter_region(args: argparse.Namespace) -> List[Dict]:
    rows = []
    tau_vals = np.linspace(args.scan_tau_min, args.scan_tau_max, args.scan_n)
    D_vals = np.linspace(args.scan_D_min, args.scan_D_max, args.scan_n)
    for tau in tau_vals:
        for D in D_vals:
            # Clone minimal namespace.
            p = argparse.Namespace(**vars(args))
            p.tau = float(tau)
            p.D = float(D)
            _, summary = evaluate(p)
            rows.append({
                "tau": tau,
                "D": D,
                "pass_Np4_cutoff_gate": summary["pass_Np4_cutoff_gate"],
                "N_p_from_retained_constraints": summary["N_p_from_retained_constraints"],
                "status": summary["status"],
            })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lmax", type=int, default=6)
    ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--nu0", type=float, default=0.05)
    ap.add_argument("--D", type=float, default=0.30)
    ap.add_argument("--Q", type=float, default=0.02)
    ap.add_argument("--kappa0", type=float, default=0.08)
    ap.add_argument("--ell-c", type=float, default=2.0)
    ap.add_argument("--p", type=float, default=2.0)
    ap.add_argument("--branches", type=int, default=12)
    ap.add_argument("--retention-margin", type=float, default=0.35, help="Constrained l=0,1 retained if growth >= -margin.")
    ap.add_argument("--suppression-margin", type=float, default=0.25, help="l>=2 suppressed if growth <= -margin.")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--scan-n", type=int, default=31)
    ap.add_argument("--scan-tau-min", type=float, default=0.2)
    ap.add_argument("--scan-tau-max", type=float, default=3.0)
    ap.add_argument("--scan-D-min", type=float, default=0.05)
    ap.add_argument("--scan-D-max", type=float, default=0.80)
    ap.add_argument("--outdir", default="outputs_delay_mode_cutoff")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows, summary = evaluate(args)
    write_csv(outdir / "delay_mode_stability_table.csv", rows)
    write_csv(outdir / "delay_mode_cutoff_summary.csv", [summary])

    if args.scan:
        scan = scan_parameter_region(args)
        write_csv(outdir / "delay_mode_cutoff_scan.csv", scan)

    report = [
        "# Pressure mode cutoff delay-stability audit",
        "",
        f"Status: **{summary['status']}**",
        f"Pass Np=4 cutoff gate: `{summary['pass_Np4_cutoff_gate']}`",
        f"Retained modes: `{summary['retained_modes']}`",
        f"Suppressed modes: `{summary['suppressed_modes']}`",
        f"N_p from retained constraints: `{summary['N_p_from_retained_constraints']}`",
        "",
        "Model:",
        "",
        "\\[",
        "\\dot a_l(t)=-\\nu_l a_l(t)+\\kappa_l a_l(t-\\tau).",
        "\\]",
        "",
        "Characteristic roots:",
        "",
        "\\[",
        "\\lambda_k=-\\nu_l+\\tau^{-1}W_k(\\tau\\kappa_l e^{\\nu_l\\tau}).",
        "\\]",
        "",
        "This is a gate-auditor. It supports N_p=4 only inside the stated delay-stability model.",
    ]
    (outdir / "delay_mode_cutoff_report.md").write_text("\n".join(report), encoding="utf-8")

    tex = r"""\section{Delay-stability pressure-mode cutoff}
The spherical pressure constraints select \(\ell=0\) and \(\ell=1\).  To test
whether higher shape modes are dynamically suppressed, model each pressure mode
by
\[
  \dot a_\ell(t)=-\nu_\ell a_\ell(t)+\kappa_\ell a_\ell(t-\tau),
\]
with
\[
  \nu_\ell=\nu_0+D\ell(\ell+1)+Q[\ell(\ell+1)]^2.
\]
The characteristic roots are
\[
  \lambda_k
  =
  -\nu_\ell+\frac{1}{\tau}
  W_k\!\left(\tau\kappa_\ell e^{\nu_\ell\tau}\right).
\]
A dynamically consistent \(N_p=4\) cutoff requires \(\ell=0,1\) to remain
retained by the pressure constraints while all \(\ell\ge2\) modes are damped
shape modes.  This script reports the pass/fail status for the stated delay
parameters and scans parameter regions if requested.
"""
    (outdir / "delay_mode_cutoff_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Pressure mode cutoff delay-stability audit")
    print("=" * 72)
    print(f"status          : {summary['status']}")
    print(f"pass gate       : {summary['pass_Np4_cutoff_gate']}")
    print(f"retained modes  : {summary['retained_modes']}")
    print(f"suppressed modes: {summary['suppressed_modes']}")
    print(f"N_p retained    : {summary['N_p_from_retained_constraints']}")
    print(f"scipy lambertw  : {SCIPY_AVAILABLE}")
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
