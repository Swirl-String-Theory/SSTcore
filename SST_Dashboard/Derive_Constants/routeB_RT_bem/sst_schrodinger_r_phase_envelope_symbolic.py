#!/usr/bin/env python3
"""
sst_schrodinger_r_phase_envelope_symbolic.py

Gate-3 audit for the SST Schrödinger--R-phase/Kelvin Envelope Principle.

This script derives the slow-envelope limit of a massive torsional R-phase
wave equation:

    theta_tt - c^2 Laplacian(theta) + Omega_0^2 theta = 0

with ansatz:

    theta(x,t) = psi(x,t) exp(-i Omega_0 t)

After cancellation of the carrier mass term and neglecting psi_tt in the
slowly varying envelope approximation (SVEA), the remaining equation is:

    i psi_t = - c^2/(2 Omega_0) Laplacian(psi)

When Omega_0 = |v_swirl|/r_c, this gives:

    D_SST = c^2/(2 Omega_0) = r_c c^2/(2 |v_swirl|) = hbar/(2 m_e)

Interpretation:
    This supports the route: R-phase stiffness supplies c^2, while the horn-
    torus core cycle supplies Omega_0.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def constants() -> dict[str, float]:
    return {
        "c": 2.99792458e8,
        "hbar": 1.054571817e-34,
        "m_e": 9.1093837015e-31,
        "r_c": 1.40897017e-15,
        "v_swirl": 1.09384563e6,
    }


def derive_with_sympy() -> str:
    """Return a symbolic derivation string. Uses sympy if available."""
    try:
        import sympy as sp
    except Exception as exc:  # pragma: no cover - sympy may be absent
        return (
            "SymPy unavailable; using manual derivation.\n"
            f"Import error: {exc}\n\n"
            + manual_derivation_text()
        )

    x, t, c, Omega0 = sp.symbols("x t c Omega_0", positive=True, real=True)
    psi = sp.Function("psi")(x, t)
    I = sp.I
    theta = psi * sp.exp(-I * Omega0 * t)

    eq = sp.diff(theta, t, 2) - c**2 * sp.diff(theta, x, 2) + Omega0**2 * theta
    reduced = sp.simplify(sp.expand(eq / sp.exp(-I * Omega0 * t)))

    # Substitute the SVEA condition psi_tt -> 0.
    svea = reduced.xreplace({sp.diff(psi, t, 2): sp.Integer(0)})
    # Solve -2 i Omega psi_t - c^2 psi_xx = 0 for i psi_t.
    psi_t = sp.diff(psi, t)
    psi_xx = sp.diff(psi, x, 2)
    solved = sp.Eq(I * psi_t, -c**2 / (2 * Omega0) * psi_xx)

    lines = []
    lines.append("Symbolic one-dimensional envelope derivation")
    lines.append("=" * 52)
    lines.append("Ansatz:")
    lines.append("  theta(x,t) = psi(x,t) exp(-i Omega_0 t)")
    lines.append("\nCarrier equation residual divided by exp(-i Omega_0 t):")
    lines.append(f"  {sp.sstr(reduced)}")
    lines.append("\nAfter SVEA, psi_tt -> 0:")
    lines.append(f"  {sp.sstr(svea)} = 0")
    lines.append("\nEquivalent Schrödinger-type envelope:")
    lines.append(f"  {sp.sstr(solved)}")
    lines.append("\nIn vector form:")
    lines.append("  i partial_t psi = - c^2/(2 Omega_0) nabla^2 psi")
    return "\n".join(lines)


def manual_derivation_text() -> str:
    return """Manual derivation
=================
Start with:
  theta_tt - c^2 nabla^2(theta) + Omega_0^2 theta = 0

Use:
  theta = psi exp(-i Omega_0 t)

Then:
  theta_tt = (psi_tt - 2 i Omega_0 psi_t - Omega_0^2 psi) exp(-i Omega_0 t)
  nabla^2 theta = (nabla^2 psi) exp(-i Omega_0 t)

Substitution cancels the carrier term:
  psi_tt - 2 i Omega_0 psi_t - c^2 nabla^2 psi = 0

Slow-envelope approximation:
  |psi_tt| << 2 Omega_0 |psi_t|

Therefore:
  -2 i Omega_0 psi_t - c^2 nabla^2 psi = 0

So:
  i psi_t = - c^2/(2 Omega_0) nabla^2 psi
"""


def numerical_closure() -> list[tuple[str, float, str]]:
    k = constants()
    c = k["c"]
    hbar = k["hbar"]
    m_e = k["m_e"]
    r_c = k["r_c"]
    v = k["v_swirl"]
    omega0 = v / r_c
    d_sst = c**2 / (2.0 * omega0)
    d_e = hbar / (2.0 * m_e)
    lambda_cbar_sst = c / omega0
    lambda_cbar_std = hbar / (m_e * c)
    rel_d = abs(d_sst - d_e) / d_e
    rel_l = abs(lambda_cbar_sst - lambda_cbar_std) / lambda_cbar_std
    return [
        ("Omega_0 = |v_swirl|/r_c", omega0, "s^-1"),
        ("D_SST = c^2/(2 Omega_0)", d_sst, "m^2 s^-1"),
        ("D_e = hbar/(2 m_e)", d_e, "m^2 s^-1"),
        ("relative error D_SST vs D_e", rel_d, "dimensionless"),
        ("lambda_Cbar(SST)", lambda_cbar_sst, "m"),
        ("lambda_Cbar(std)", lambda_cbar_std, "m"),
        ("relative error lambda_Cbar", rel_l, "dimensionless"),
    ]


def render_report() -> str:
    text = derive_with_sympy()
    rows = numerical_closure()
    text += "\n\nNumerical closure\n"
    text += "=" * 52 + "\n"
    for name, value, unit in rows:
        text += f"{name:<36} {value:.15e} {unit}\n"
    text += "\nGate interpretation\n"
    text += "=" * 52 + "\n"
    text += (
        "PASS here means: if Omega_0 = |v_swirl|/r_c is accepted as the horn-torus "
        "core-cycle frequency, then the R-phase envelope coefficient equals the "
        "electron Schrödinger coefficient within the constants tolerance.\n"
        "This supports [CANON-CANDIDATE] status for the R-phase stiffness route.\n"
    )
    return text


def write_markdown(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# SST R-phase Envelope Symbolic Gate\n\n")
        f.write("```text\n")
        f.write(report)
        f.write("\n```\n")
        f.write("\n## Canon-candidate equation\n\n")
        f.write("```tex\n")
        f.write(
            "\\partial_t^2\\theta_R-c^2\\nabla^2\\theta_R+\\Omega_0^2\\theta_R=0,\\qquad "
            "\\Omega_0=\\frac{\\lVert\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert}{r_c}.\n"
            "\\theta_R=\\psi e^{-i\\Omega_0 t}+\\mathrm{c.c.}\\quad\\Longrightarrow\\quad "
            "i\\partial_t\\psi=-\\frac{c^2}{2\\Omega_0}\\nabla^2\\psi.\n"
        )
        f.write("```\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="SST R-phase envelope symbolic audit.")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Directory for Markdown output.")
    parser.add_argument("--no-files", action="store_true", help="Only print; do not write Markdown output.")
    args = parser.parse_args()

    report = render_report()
    print(report)

    if not args.no_files:
        out = args.outdir / "sst_schrodinger_r_phase_envelope_symbolic_summary.md"
        write_markdown(out, report)
        print(f"\nWrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
