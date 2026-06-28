#!/usr/bin/env python3
"""
solve_one_cell_hodge_phase_hessian.py

One-cell Hodge/Dirichlet-to-Neumann phase-Hessian solver on a spherical cell.

Purpose
-------
This script computes the exterior harmonic phase Hessian by spherical-harmonic
mode.  It is a genuine one-cell Hodge boundary calculation for the scalar
phase sector:

    u_lm(r,Omega) = phi_lm (R/r)^(l+1) Y_lm(Omega).

For each l,

    ∫_{r>=R} |∇u_lm|² d³x = R (l+1) |phi_lm|²

for orthonormal spherical harmonics.  For the real constant boundary phase
u(R)=phi, this reduces to

    ∫ |∇u|² d³x = 4π R phi².

The Hessian relation is

    Lambda_l = K_cell R (l+1)

in orthonormal mode amplitudes, or

    Lambda_constant = 4π R K_cell

for the constant physical boundary phase.

The script can then compare an independently supplied interior cell Hessian
Lambda_phi to E_eff/2.  If Lambda_phi is supplied by measurement or another
operator, K_cell follows as Lambda_phi/(4πR).

Epistemic status
----------------
Derived:
  * q_phi = dim H^0(S^2) = 1,
  * only l=0 gives 1/r far field,
  * exterior capacity/Hodge Hessian.

Open unless supplied:
  * Lambda_phi = E_eff/2 from the interior finite-cell operator.

Usage
-----
    python solve_one_cell_hodge_phase_hessian.py --outdir outputs_hodge_phase

Conditional target:
    python solve_one_cell_hodge_phase_hessian.py --E-eff 274.0748756568 --lambda-source Eeff_over_2

Measured operator:
    python solve_one_cell_hodge_phase_hessian.py --lambda-source measured --lambda-value 137.0374378284
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


def mode_table(lmax: int, R: float, K_cell: float) -> List[Dict]:
    rows = []
    for l in range(lmax + 1):
        degeneracy = 2*l + 1
        # Orthonormal Y_lm boundary amplitude Hessian:
        capacity_l = R * (l + 1)
        lambda_l = K_cell * capacity_l
        rows.append({
            "ell": l,
            "degeneracy": degeneracy,
            "exterior_decay": f"r^-{l+1}",
            "capacity_eigenvalue_R_lplus1": capacity_l,
            "lambda_l_for_Kcell": lambda_l,
            "contributes_to_1_over_r": l == 0,
            "status": "leading_H0_Coulombic" if l == 0 else "subleading_multipole",
        })
    return rows


def constant_capacity(R: float) -> float:
    # Physical constant boundary phase u(R)=phi, not normalized Y_00 amplitude.
    return 4.0 * math.pi * R


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=float, default=1.0)
    ap.add_argument("--lmax", type=int, default=8)
    ap.add_argument("--K-cell", type=float, default=1.0, help="Reference K_cell for mode table.")
    ap.add_argument("--E-eff", type=float, default=None)
    ap.add_argument("--lambda-source", choices=["none", "Eeff_over_2", "measured"], default="none")
    ap.add_argument("--lambda-value", type=float, default=None)
    ap.add_argument("--outdir", default="outputs_hodge_phase_hessian")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    modes = mode_table(args.lmax, args.radius, args.K_cell)
    write_csv(outdir / "hodge_phase_mode_table.csv", modes)

    cap_const = constant_capacity(args.radius)
    q_phi = 1

    if args.lambda_source == "Eeff_over_2":
        if args.E_eff is None:
            raise SystemExit("--lambda-source Eeff_over_2 requires --E-eff")
        Lambda = args.E_eff / 2.0
        source_status = "CONDITIONAL_TARGET_EEFF_OVER_2"
    elif args.lambda_source == "measured":
        if args.lambda_value is None:
            raise SystemExit("--lambda-source measured requires --lambda-value")
        Lambda = args.lambda_value
        source_status = "INDEPENDENT_IF_MEASURED_OPERATOR_NOT_NORMALIZED_TO_ALPHA"
    else:
        Lambda = None
        source_status = "NO_INTERIOR_HESSIAN_SUPPLIED"

    if Lambda is not None:
        K_from_constant = Lambda / cap_const
        if args.E_eff is not None:
            K_target = args.E_eff / (8.0 * math.pi * args.radius)
            target_match = abs(K_from_constant - K_target) / max(abs(K_target), 1e-30)
        else:
            K_target = None
            target_match = None
    else:
        K_from_constant = None
        K_target = None
        target_match = None

    gates = [
        {
            "gate": "H0_dimension",
            "claim": "q_phi=dim H^0(S^2)=1",
            "value": q_phi,
            "status": "DERIVED",
            "notes": "S^2 connected; single constant boundary phase mode.",
        },
        {
            "gate": "far_field_selection",
            "claim": "only ell=0 contributes to 1/r",
            "value": "ell=0",
            "status": "DERIVED",
            "notes": "ell>=1 decays as r^-(ell+1), hence O(r^-2) or faster.",
        },
        {
            "gate": "constant_phase_capacity",
            "claim": "capacity=4*pi*R",
            "value": cap_const,
            "status": "DERIVED",
            "notes": "Direct Hodge/Dirichlet-to-Neumann exterior calculation.",
        },
        {
            "gate": "K_cell_from_interior_Hessian",
            "claim": "K_cell=Lambda_phi/(4*pi*R)",
            "value": K_from_constant,
            "status": source_status,
            "notes": "Requires independently supplied Lambda_phi.",
        },
        {
            "gate": "Eeff_over_2_target",
            "claim": "Lambda_phi=E_eff/2",
            "value": Lambda,
            "status": "OPEN_OPERATOR_GATE" if args.lambda_source == "none" else source_status,
            "notes": "Must come from interior one-cell operator, not far-field normalization.",
        },
    ]
    write_csv(outdir / "hodge_phase_hessian_gates.csv", gates)

    summary = [{
        "radius": args.radius,
        "q_phi": q_phi,
        "constant_capacity": cap_const,
        "lambda_source": args.lambda_source,
        "Lambda_phi": Lambda,
        "K_cell_from_Lambda": K_from_constant,
        "E_eff": args.E_eff,
        "K_target_Eeff_over_8piR": K_target,
        "relative_match_to_Eeff_over_8piR": target_match,
    }]
    write_csv(outdir / "hodge_phase_hessian_summary.csv", summary)

    report = f"""# One-cell Hodge phase-Hessian solver

Radius:

\\[
R={args.radius}.
\\]

The physical constant boundary phase has exterior capacity

\\[
C_0=4\\pi R={cap_const:.12g}.
\\]

Thus

\\[
\\Lambda_\\phi=4\\pi R K_{{\\rm cell}}.
\\]

Only the \(\\ell=0\) mode contributes to the leading \(1/r\) far-field, so

\\[
q_\\phi=\\dim H^0(S^2)=1.
\\]

Interior Hessian source: `{args.lambda_source}`.

If an independent operator gives \(\\Lambda_\\phi=E_{{\\rm eff}}/2\), then

\\[
K_{{\\rm cell}}=\\frac{{E_{{\\rm eff}}}}{{8\\pi R}}.
\\]

Current K from supplied Lambda:

`{K_from_constant}`.
"""
    (outdir / "hodge_phase_hessian_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{One-cell Hodge phase-Hessian}
For an exterior harmonic phase mode
\[
  u_{\ell m}(r,\Omega)=\phi_{\ell m}\left(\frac{R}{r}\right)^{\ell+1}Y_{\ell m}(\Omega),
\]
the exterior Dirichlet-to-Neumann energy is
\[
  \int_{r\ge R}|\nabla u_{\ell m}|^2\,d^3x
  =
  R(\ell+1)|\phi_{\ell m}|^2
\]
for orthonormal spherical harmonics.  Only \(\ell=0\) produces a \(1/r\)
far-field.  For the physical constant boundary phase \(u(R)=\phi\),
\[
  \int_{r\ge R}|\nabla u|^2\,d^3x=4\pi R\phi^2.
\]
Consequently,
\[
  \Lambda_\phi=4\pi R K_{\rm cell}.
\]
Since \(S^2\) is connected,
\[
  q_\phi=\dim H^0(S^2)=1.
\]
If an independent interior one-cell operator gives
\[
  \Lambda_\phi=\frac{E_{\rm eff}}2,
\]
then
\[
  K_{\rm cell}=\frac{E_{\rm eff}}{8\pi R}.
\]
For \(R=1\), this reduces to \(K_{\rm cell}=E_{\rm eff}/(8\pi)\).
"""
    (outdir / "hodge_phase_hessian_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("One-cell Hodge phase-Hessian solver")
    print("=" * 72)
    print(f"q_phi             : {q_phi}")
    print(f"constant capacity : {cap_const:.12g}")
    print(f"lambda source     : {args.lambda_source}")
    print(f"Lambda_phi        : {Lambda}")
    print(f"K_cell            : {K_from_constant}")
    print(f"status            : {source_status}")
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
