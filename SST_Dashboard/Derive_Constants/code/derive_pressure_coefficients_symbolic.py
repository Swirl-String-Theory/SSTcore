#!/usr/bin/env python3
"""
derive_pressure_coefficients_symbolic.py

Symbolic derivation-target audit for the pressure-cell coefficients

    16*pi/3, 11/48, chi_R=2, and K_cell=E_eff/(8*pi).

This script does NOT pretend to prove these coefficients from microscopic
physics.  It does something more precise and reviewer-safe:

1. Defines a general spherical shell pressure action with unknown mode counts
   and shell coefficients.
2. Expands the pressure scale to second order in eta_K.
3. Shows exactly which geometric/mode-count assumptions are sufficient to give

       E_p^(0) = (16*pi/3) L_K,
       E_p^NLS = (16*pi/3) L_K [1 - 11/(48 L_K^2)],
       chi_R = 2,
       K_cell = E_eff/(8*pi).

4. Exports CSV/Markdown tables that classify each coefficient as:
       theorem / conditional lemma / open gate.

The goal is to make the remaining "derived" gates explicit.

Typical usage
-------------
    python derive_pressure_coefficients_symbolic.py --outdir outputs_symbolic_pressure_coefficients

With custom assumptions:
    python derive_pressure_coefficients_symbolic.py --N-pressure 4 --sigma-volume 3 --sigma-transverse 1 --chi-ratio-stiffness 4
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, List

import pandas as pd
import sympy as sp


def symbolic_derivation(args) -> Dict[str, object]:
    L, eta, chi, Np, sigma, sigma_v, sigma_t, lam, qphi = sp.symbols(
        "L eta chi_R N_p sigma sigma_v sigma_t lambda_chi q_phi",
        positive=True,
    )

    V3 = sp.Rational(4, 3) * sp.pi

    # Lemma 1: zeroth pressure volume factor.
    Ep0_general = sp.simplify(Np * V3 * L)
    Np_required = sp.solve(sp.Eq(Ep0_general, sp.Rational(16, 3) * sp.pi * L), Np)[0]

    # Cell shell parameter.
    eta_general = sp.simplify(1 / (2 * chi * L))

    # Lemma 2: shell correction.
    # General correction: 1 - sigma eta^2.
    Ep_shell_general = sp.simplify(Ep0_general * (1 - sigma * eta_general**2))
    # coefficient c2 in 1 - c2/L^2
    c2_general = sp.simplify(sigma / (4 * chi**2))
    sigma_required_for_11_48_at_chi2 = sp.solve(
        sp.Eq(c2_general.subs(chi, 2), sp.Rational(11, 48)), sigma
    )[0]

    # Proposed decomposition sigma = 3 + 2/3.
    angular_transverse_average = sp.Rational(2, 3)
    sigma_decomposed = sp.simplify(sigma_v + sigma_t * angular_transverse_average)
    sigma_decomposed_value = sigma_decomposed.subs({
        sigma_v: sp.Rational(args.sigma_volume),
        sigma_t: sp.Rational(args.sigma_transverse),
    })
    c2_decomposed_chi2 = sp.simplify(c2_general.subs({
        sigma: sigma_decomposed_value,
        chi: 2,
    }))

    # Lemma 3 / chi_R gate: model A_chi = chi + lambda/chi.
    A_chi = chi + lam / chi
    dA_dchi = sp.diff(A_chi, chi)
    chi_stationary = sp.solve(sp.Eq(dA_dchi, 0), chi)[0]
    lam_required_for_chi2 = sp.solve(sp.Eq(chi_stationary, 2), lam)[0]

    # Phase Hessian gate: A_phi = q_phi E_eff phi^2/4.
    # Lambda_phi = q_phi E_eff/2.  K = Lambda/(4pi).
    q_required = sp.solve(sp.Eq(qphi, 1), qphi)[0]

    assumptions = {
        "N_pressure": sp.Rational(args.N_pressure),
        "sigma_volume": sp.Rational(args.sigma_volume),
        "sigma_transverse": sp.Rational(args.sigma_transverse),
        "chi_ratio_stiffness_lambda": sp.Rational(args.chi_ratio_stiffness),
        "q_phi": sp.Rational(args.q_phi),
    }

    Ep0_assumed = sp.simplify(Ep0_general.subs(Np, assumptions["N_pressure"]))
    chi_assumed = sp.simplify(chi_stationary.subs(lam, assumptions["chi_ratio_stiffness_lambda"]))
    sigma_assumed = sp.simplify(sigma_decomposed.subs({
        sigma_v: assumptions["sigma_volume"],
        sigma_t: assumptions["sigma_transverse"],
    }))
    c2_assumed = sp.simplify(c2_general.subs({sigma: sigma_assumed, chi: chi_assumed}))
    Ep_shell_assumed = sp.simplify(Ep0_assumed * (1 - c2_assumed / L**2))
    qphi_assumed = assumptions["q_phi"]

    gates: List[Dict[str, object]] = [
        {
            "gate": "pressure volume prefactor",
            "target": "16*pi/3",
            "general_formula": str(Ep0_general / L),
            "sufficient_assumption": "N_p=4 pressure sectors",
            "required_value": str(Np_required),
            "assumed_value": str(assumptions["N_pressure"]),
            "result": str(sp.simplify(Ep0_assumed / L)),
            "status": "passed_if_Np_derived" if assumptions["N_pressure"] == Np_required else "failed",
            "remaining_task": "derive N_p=4 from a pressure-cell mode count or variational principle",
        },
        {
            "gate": "finite-shell correction",
            "target": "11/48",
            "general_formula": "c2=sigma/(4 chi_R^2)",
            "sufficient_assumption": "chi_R=2 and sigma=3+2/3=11/3",
            "required_value": "sigma=11/3 at chi_R=2",
            "assumed_value": f"sigma={sigma_assumed}, chi_R={chi_assumed}",
            "result": str(c2_assumed),
            "status": "passed_if_sigma_decomposition_derived" if c2_assumed == sp.Rational(11, 48) else "failed",
            "remaining_task": "derive sigma=3+2/3 from controlled NLS/GP shell second variation",
        },
        {
            "gate": "cell-radius closure",
            "target": "chi_R=2",
            "general_formula": "A_chi=chi_R+lambda_chi/chi_R -> chi_R=sqrt(lambda_chi)",
            "sufficient_assumption": "lambda_chi=4",
            "required_value": str(lam_required_for_chi2),
            "assumed_value": str(assumptions["chi_ratio_stiffness_lambda"]),
            "result": str(chi_assumed),
            "status": "passed_if_lambda_chi_derived" if chi_assumed == 2 else "failed",
            "remaining_task": "derive lambda_chi=4 from inner/outer pressure-cell stationarity",
        },
        {
            "gate": "phase stiffness normalization",
            "target": "K_cell=E_eff/(8*pi)",
            "general_formula": "A_phi=q_phi E_eff phi^2/4 -> Lambda=q_phi E_eff/2",
            "sufficient_assumption": "q_phi=1 canonical unit phase normalization",
            "required_value": str(q_required),
            "assumed_value": str(qphi_assumed),
            "result": "K_cell=E_eff/(8*pi)" if qphi_assumed == 1 else f"K_cell={qphi_assumed} E_eff/(8*pi)",
            "status": "passed_if_phase_hessian_derived" if qphi_assumed == 1 else "failed",
            "remaining_task": "derive q_phi=1 from one-cell phase-Hessian operator, not by normalization",
        },
    ]

    expressions = {
        "V3": V3,
        "Ep0_general": Ep0_general,
        "Np_required": Np_required,
        "eta_general": eta_general,
        "Ep_shell_general": Ep_shell_general,
        "c2_general": c2_general,
        "sigma_required_for_11_48_at_chi2": sigma_required_for_11_48_at_chi2,
        "sigma_decomposition": sigma_decomposed,
        "sigma_decomposition_value": sigma_decomposed_value,
        "c2_decomposed_chi2": c2_decomposed_chi2,
        "A_chi": A_chi,
        "chi_stationary": chi_stationary,
        "lambda_required_for_chi2": lam_required_for_chi2,
        "Ep0_assumed": Ep0_assumed,
        "chi_assumed": chi_assumed,
        "sigma_assumed": sigma_assumed,
        "c2_assumed": c2_assumed,
        "Ep_shell_assumed": Ep_shell_assumed,
    }

    return {"gates": gates, "expressions": expressions}


def write_latex_summary(outdir: Path, expressions: Dict[str, object], gates: List[Dict[str, object]]) -> None:
    rows = []
    for g in gates:
        rows.append(
            f"{g['gate']} & {g['target']} & {g['sufficient_assumption']} & {g['status']} \\\\"
        )
    table_rows = "\n".join(rows)

    tex = rf"""\section{{Symbolic pressure-coefficient audit}}
\label{{sec:symbolic-pressure-audit}}

The symbolic audit uses the general zeroth-order pressure scale
\[
  E_p^{{(0)}} = N_p \frac{{4\pi}}{{3}}\mathcal L_K .
\]
The target value \(E_p^{{(0)}}=(16\pi/3)\mathcal L_K\) is obtained iff
\[
  N_p = {sp.latex(expressions['Np_required'])}.
\]
Thus the coefficient \(16\pi/3\) is derived only after deriving the
four-sector pressure count \(N_p=4\).

For the shell correction, with
\[
  \eta_K = \frac{{1}}{{2\chi_R\mathcal L_K}},
\]
write
\[
  E_p^{{\rm shell}}
  =
  E_p^{{(0)}}\left(1-\sigma\eta_K^2\right)
  =
  E_p^{{(0)}}\left[
  1-\frac{{\sigma}}{{4\chi_R^2\mathcal L_K^2}}
  \right].
\]
At \(\chi_R=2\), the target coefficient \(11/48\) requires
\[
  \sigma = {sp.latex(expressions['sigma_required_for_11_48_at_chi2'])}.
\]
The proposed second-variation decomposition is
\[
  \sigma = 3 + \frac{{2}}{{3}} = \frac{{11}}{{3}},
\]
where the \(3\) term is assigned to the spherical volume second variation and
the \(2/3\) term to isotropic transverse averaging.  This is a derivation target:
the decomposition must be obtained from a controlled shell/NLS calculation to
upgrade the coefficient from closure hypothesis to derived result.

The radius closure is represented by the minimal action
\[
  A_\chi=\chi_R+\frac{{\lambda_\chi}}{{\chi_R}},
\]
whose stationary point is
\[
  \chi_R=\sqrt{{\lambda_\chi}}.
\]
Therefore \(\chi_R=2\) requires
\[
  \lambda_\chi = {sp.latex(expressions['lambda_required_for_chi2'])}.
\]

\begin{{table}}[h]
\centering
\caption{{Symbolic gates for the pressure-cell derived label.}}
\begin{{tabular}}{{@{{}}llll@{{}}}}
\toprule
Gate & Target & Sufficient assumption & Status\\
\midrule
{table_rows}
\bottomrule
\end{{tabular}}
\end{{table}}
"""
    (outdir / "symbolic_pressure_audit_snippet.tex").write_text(tex, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N-pressure", type=int, default=4, help="Pressure-sector count N_p; target is 4.")
    parser.add_argument("--sigma-volume", type=int, default=3, help="Volume second-variation contribution; target 3.")
    parser.add_argument("--sigma-transverse", type=int, default=1, help="Weight multiplying <sin^2>=2/3; target 1.")
    parser.add_argument("--chi-ratio-stiffness", type=int, default=4, help="lambda_chi in A_chi=chi+lambda/chi; target 4.")
    parser.add_argument("--q-phi", type=int, default=1, help="Phase-Hessian normalization q_phi; target 1.")
    parser.add_argument("--outdir", default="outputs_symbolic_pressure_coefficients")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    result = symbolic_derivation(args)
    gates = result["gates"]
    expressions = result["expressions"]

    pd.DataFrame(gates).to_csv(outdir / "derived_coefficient_gates.csv", index=False)

    expr_rows = [{"name": k, "sympy": str(v), "latex": sp.latex(v)} for k, v in expressions.items()]
    pd.DataFrame(expr_rows).to_csv(outdir / "symbolic_expressions.csv", index=False)

    write_latex_summary(outdir, expressions, gates)

    md = ["# Symbolic pressure coefficient audit", ""]
    for g in gates:
        md.append(f"## {g['gate']}")
        md.append(f"- Target: `{g['target']}`")
        md.append(f"- General formula: `{g['general_formula']}`")
        md.append(f"- Sufficient assumption: `{g['sufficient_assumption']}`")
        md.append(f"- Result: `{g['result']}`")
        md.append(f"- Status: **{g['status']}**")
        md.append(f"- Remaining task: {g['remaining_task']}")
        md.append("")
    (outdir / "derived_coefficient_gates.md").write_text("\n".join(md), encoding="utf-8")

    print(pd.DataFrame(gates).to_string(index=False))
    print(f"\nWrote {outdir/'derived_coefficient_gates.csv'}")
    print(f"Wrote {outdir/'symbolic_expressions.csv'}")
    print(f"Wrote {outdir/'symbolic_pressure_audit_snippet.tex'}")
    print(f"Wrote {outdir/'derived_coefficient_gates.md'}")


if __name__ == "__main__":
    main()
