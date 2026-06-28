#!/usr/bin/env python3
"""
derive_phase_pressure_exchange_self_duality.py

Final-gate attempt: derive the phase-pressure half-budget identity

    M_phi = M_p = E_eff/2

from canonical linearized GP/Madelung dynamics.

Core statement
--------------
For the linearized Madelung/GP Hamiltonian, density/pressure perturbation and
phase are a canonical pair.  Each normal mode is a harmonic oscillator,

    H_k = 1/2 p_k^2 + 1/2 omega_k^2 q_k^2.

The phase/flow sector and pressure/compression sector are the kinetic and
potential parts of this oscillator.  For every periodic normal mode,

    <1/2 p_k^2>_T = <1/2 omega_k^2 q_k^2>_T.

Therefore the cycle-averaged quadratic budget is split equally:

    M_phi = M_p = E_eff/2.

This derives gamma=1 inside the canonical linearized normal-mode reduction.

What remains outside this script
--------------------------------
To claim a primitive SST derivation, one must show that the finite-cell
E_eff budget is indeed the cycle-averaged quadratic energy of a single
canonical interior normal-mode family, and that non-Hamiltonian/dissipative or
noncanonical cross terms are absent or higher order.

Usage
-----
    python derive_phase_pressure_exchange_self_duality.py --outdir outputs_phase_pressure_self_duality

Sensitivity:
    python derive_phase_pressure_exchange_self_duality.py --noncanonical-gamma 1.05
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


def oscillator_average(omega: float, amplitude: float, n_grid: int):
    T = 2.0*math.pi/omega
    t = np.linspace(0.0, T, n_grid, endpoint=False)
    q = amplitude*np.cos(omega*t)
    p = -amplitude*omega*np.sin(omega*t)
    E_pressure = 0.5*omega*omega*q*q
    E_phase = 0.5*p*p
    return {
        "omega": omega,
        "amplitude": amplitude,
        "avg_phase": float(np.mean(E_phase)),
        "avg_pressure": float(np.mean(E_pressure)),
        "gamma_avg_phase_over_pressure": float(np.mean(E_phase)/np.mean(E_pressure)),
        "total_avg": float(np.mean(E_phase + E_pressure)),
        "max_instantaneous_phase": float(np.max(E_phase)),
        "max_instantaneous_pressure": float(np.max(E_pressure)),
    }


def evaluate(Eeff: float, L: float, R: float, a: float | None, gamma_noncanonical: float, n_grid: int):
    if a is None:
        a = 1.0/(4.0*L)
    Racc = R-a
    f_area = (Racc/R)**2

    # Canonical self-dual split.
    M_phi = Eeff/2.0
    M_p = Eeff/2.0
    M_acc = M_phi*f_area
    Lambda = M_acc/(Racc*Racc)

    # Noncanonical sensitivity split with gamma = M_phi/M_p.
    gamma = gamma_noncanonical
    M_phi_nc = gamma*Eeff/(1.0+gamma)
    M_p_nc = Eeff/(1.0+gamma)
    Lambda_nc = (M_phi_nc*f_area)/(Racc*Racc)

    return {
        "E_eff": Eeff,
        "E_eff_over_2": Eeff/2.0,
        "L_K": L,
        "a": a,
        "R": R,
        "R_accessible": Racc,
        "accessible_area_fraction": f_area,
        "M_phi_canonical": M_phi,
        "M_pressure_canonical": M_p,
        "gamma_canonical": M_phi/M_p,
        "M_accessible": M_acc,
        "Lambda_phi": Lambda,
        "Lambda_over_Eeff_over_2": Lambda/(Eeff/2.0),
        "noncanonical_gamma": gamma,
        "M_phi_noncanonical": M_phi_nc,
        "M_pressure_noncanonical": M_p_nc,
        "Lambda_noncanonical": Lambda_nc,
        "Lambda_noncanonical_over_target": Lambda_nc/(Eeff/2.0),
        "status": "PHASE_PRESSURE_HALF_BUDGET_DERIVED_WITHIN_CANONICAL_NORMAL_MODE_REDUCTION",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--E-eff", type=float, default=274.0748756568)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--R", type=float, default=1.0)
    ap.add_argument("--a", type=float, default=None)
    ap.add_argument("--n-grid", type=int, default=20000)
    ap.add_argument("--noncanonical-gamma", type=float, default=1.05)
    ap.add_argument("--outdir", default="outputs_phase_pressure_self_duality")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary = evaluate(args.E_eff, args.L_K, args.R, args.a, args.noncanonical_gamma, args.n_grid)
    write_csv(outdir/"phase_pressure_self_duality_summary.csv", [summary])

    osc_rows = []
    for omega, amp in [(0.5, 1.0), (1.0, 1.0), (3.0, 0.7), (10.0, 0.2)]:
        osc_rows.append(oscillator_average(omega, amp, args.n_grid))
    write_csv(outdir/"canonical_oscillator_equipartition.csv", osc_rows)

    sens = []
    for gamma in [0.5, 0.75, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5, args.noncanonical_gamma]:
        res = evaluate(args.E_eff, args.L_K, args.R, args.a, gamma, args.n_grid)
        sens.append({
            "gamma": gamma,
            "M_phi_over_Eeff": res["M_phi_noncanonical"]/args.E_eff,
            "M_pressure_over_Eeff": res["M_pressure_noncanonical"]/args.E_eff,
            "Lambda_over_target": res["Lambda_noncanonical_over_target"],
            "relative_error_Lambda": res["Lambda_noncanonical_over_target"] - 1.0,
        })
    write_csv(outdir/"phase_pressure_self_duality_sensitivity.csv", sens)

    theorem = [
        {
            "step": "Madelung_canonical_pair",
            "formula": "delta n and theta are canonically conjugate in the linearized GP/Madelung action",
            "status": "standard Hamiltonian hydrodynamic structure",
        },
        {
            "step": "normal_mode_reduction",
            "formula": "H_k = 1/2 p_k^2 + 1/2 omega_k^2 q_k^2",
            "status": "derived after diagonalizing the quadratic Hamiltonian",
        },
        {
            "step": "cycle_virial",
            "formula": "<1/2 p_k^2> = <1/2 omega_k^2 q_k^2>",
            "status": "derived for each periodic harmonic normal mode",
        },
        {
            "step": "half_budget",
            "formula": "M_phi = M_p = E_eff/2",
            "status": "derived within canonical normal-mode reduction",
        },
        {
            "step": "accessible_area_and_radial_optimum",
            "formula": "M_acc=M_phi(R-a)^2/R^2 and Lambda=M_acc/(R-a)^2",
            "status": "from previous gate scripts",
        },
        {
            "step": "phase_Hessian_gate",
            "formula": "Lambda_phi=E_eff/(2R^2), hence E_eff/2 for R=1",
            "status": "closed within canonical normal-mode + accessible-area + radial-optimum reduction",
        },
        {
            "step": "remaining_primitive_requirement",
            "formula": "finite-cell E_eff must be the cycle-averaged quadratic energy of this canonical interior mode family",
            "status": "physical identification still to be justified in SST primitive equations",
        },
    ]
    write_csv(outdir/"phase_pressure_self_duality_theorem_steps.csv", theorem)

    report = f"""# Phase-pressure exchange self-duality gate

## Canonical normal-mode derivation

The linearized GP/Madelung Hamiltonian reduces mode by mode to

\\[
H_k=\\frac12p_k^2+\\frac12\\omega_k^2 q_k^2.
\\]

For a periodic normal mode,

\\[
\\left\\langle\\frac12p_k^2\\right\\rangle_T
=
\\left\\langle\\frac12\\omega_k^2 q_k^2\\right\\rangle_T.
\\]

Identifying the phase/flow sector with the kinetic part and the
pressure/compression sector with the potential part gives

\\[
M_\\phi=M_p=\\frac{{E_{{eff}}}}{{2}}.
\\]

## Numerical values

\\[
E_{{eff}}={args.E_eff:.12g},
\\qquad
M_\\phi=M_p={summary['M_phi_canonical']:.12g}.
\\]

With the accessible-area projection and radial optimum,

\\[
\\Lambda_\\phi={summary['Lambda_phi']:.12g},
\\qquad
\\frac{{\\Lambda_\\phi}}{{E_{{eff}}/2}}={summary['Lambda_over_Eeff_over_2']:.12g}.
\\]

## Sensitivity

For a noncanonical split \\(\\gamma={args.noncanonical_gamma}\\),

\\[
\\frac{{\\Lambda_\\phi}}{{E_{{eff}}/2}}
=
{summary['Lambda_noncanonical_over_target']:.12g}.
\\]

## Status

`{summary['status']}`

This closes the half-budget gate inside the canonical linearized normal-mode
reduction.  The remaining physical identification is that the finite-cell
\(E_{{eff}}\) used in the pressure-cell chain is the cycle-averaged quadratic
energy of the same canonical interior mode family.
"""
    (outdir/"phase_pressure_self_duality_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Phase--pressure half-budget from canonical normal modes}
\label{app:phase-pressure-self-duality}

In the Madelung form of the GP/NLS action, the density perturbation and phase
are canonically conjugate variables.  After linearization and diagonalization,
each normal mode has Hamiltonian
\[
  H_k
  =
  \frac12p_k^2+\frac12\omega_k^2q_k^2.
\]
For the periodic solution
\[
  q_k(t)=A_k\cos(\omega_k t),
  \qquad
  p_k(t)=-A_k\omega_k\sin(\omega_k t),
\]
one has the cycle identity
\[
  \left\langle\frac12p_k^2\right\rangle_T
  =
  \left\langle\frac12\omega_k^2q_k^2\right\rangle_T.
\]
Identifying the phase/flow budget with the kinetic part and the
pressure/compression budget with the potential part gives
\[
  M_\phi=M_p.
\]
Since
\[
  E_{\rm eff}=M_\phi+M_p,
\]
it follows that
\[
  M_\phi=M_p=\frac{E_{\rm eff}}2.
\]
Together with the accessible-area projection and the radial optimum,
\[
  M_{\rm acc}=M_\phi\frac{(R-a)^2}{R^2},
  \qquad
  \Lambda_\phi=\frac{M_{\rm acc}}{(R-a)^2},
\]
one obtains
\[
  \Lambda_\phi=\frac{E_{\rm eff}}{2R^2}.
\]
For the normalized cell \(R=1\),
\[
  \Lambda_\phi=\frac{E_{\rm eff}}2.
\]
Thus the phase-Hessian gate is closed within the canonical linearized
normal-mode reduction.  The remaining physical identification is that the
finite-cell \(E_{\rm eff}\) entering the pressure-cell chain is the
cycle-averaged quadratic energy of this same canonical interior mode family.
"""
    (outdir/"phase_pressure_self_duality_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Phase-pressure exchange self-duality gate")
    print("="*72)
    print(f"E_eff                  : {args.E_eff:.12g}")
    print(f"M_phi=M_pressure       : {summary['M_phi_canonical']:.12g}")
    print(f"Lambda_phi             : {summary['Lambda_phi']:.12g}")
    print(f"Lambda/(E_eff/2)       : {summary['Lambda_over_Eeff_over_2']:.12g}")
    print(f"noncanonical gamma     : {args.noncanonical_gamma:.12g}")
    print(f"noncanonical ratio     : {summary['Lambda_noncanonical_over_target']:.12g}")
    print(f"status                 : {summary['status']}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
