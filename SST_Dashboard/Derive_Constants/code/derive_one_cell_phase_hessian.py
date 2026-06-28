#!/usr/bin/env python3
"""
derive_one_cell_phase_hessian.py

One-cell phase-Hessian gate for the finite-cell far-field coupling.

Derives the exterior geometry/operator identities:
  q_phi = dim H^0(S^2) = 1,
  int_{r>=R} |grad(phi R/r)|^2 d^3x = 4*pi*R*phi^2,
  Lambda_phi = 4*pi*R*K_cell.

Then audits the final step K_cell = E_eff/(8*pi*R). This final step requires
an independently obtained one-cell interior Hessian Lambda_phi=E_eff/2.
Without such input, the script labels the result as exterior-capacity-derived
but internally conditional.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import sympy as sp


def exterior_energy_constant_mode(R: sp.Expr):
    r, phi = sp.symbols("r phi", positive=True, real=True)
    u = phi * R / r
    du_dr = sp.diff(u, r)
    integral = sp.integrate(4 * sp.pi * r**2 * du_dr**2, (r, R, sp.oo))
    return {
        "u": sp.simplify(u),
        "du_dr": sp.simplify(du_dr),
        "energy_integral": sp.simplify(integral),
        "capacity": sp.simplify(integral / phi**2),
    }


def multipole_decay_table(lmax: int) -> pd.DataFrame:
    rows = []
    for ell in range(lmax + 1):
        rows.append({
            "ell": ell,
            "degeneracy_2ell_plus_1": 2 * ell + 1,
            "exterior_decay": f"r^-{ell+1}",
            "contributes_to_1_over_r": ell == 0,
            "far_field_status": "leading Coulombic monopole" if ell == 0 else "subleading multipole",
        })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=float, default=1.0, help="Cell boundary radius R.")
    ap.add_argument("--lmax", type=int, default=4, help="Multipole table cutoff.")
    ap.add_argument("--E-eff", type=float, default=None, help="Optional E_eff for K_cell=E_eff/(8*pi*R).")
    ap.add_argument("--lambda-value", type=float, default=None, help="Independent numerical Lambda_phi, if available.")
    ap.add_argument("--lambda-source", choices=["none", "Eeff_over_2", "measured_operator"], default="none")
    ap.add_argument("--outdir", default="outputs_phase_hessian")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    R = sp.Symbol("R", positive=True)
    phi, K, Eeff, Lambda = sp.symbols("phi K_cell E_eff Lambda_phi", positive=True, real=True)
    ext = exterior_energy_constant_mode(R)

    A_far = sp.simplify(K / 2 * ext["energy_integral"])
    Lambda_from_K = sp.simplify(sp.diff(A_far, phi, 2))
    K_from_Lambda = sp.simplify(Lambda / (4 * sp.pi * R))

    if args.lambda_source == "Eeff_over_2":
        K_expr = sp.simplify(Eeff / (8 * sp.pi * R))
        K_numeric = None if args.E_eff is None else float(args.E_eff / (8 * sp.pi.evalf() * args.radius))
        status = "conditional_on_independent_Eeff_over_2"
    elif args.lambda_source == "measured_operator":
        if args.lambda_value is None:
            raise SystemExit("--lambda-source measured_operator requires --lambda-value")
        K_expr = sp.simplify(Lambda / (4 * sp.pi * R))
        K_numeric = float(args.lambda_value / (4 * sp.pi.evalf() * args.radius))
        status = "independent_if_lambda_value_was_measured_without_far_field_matching"
    else:
        K_expr = K_from_Lambda
        K_numeric = None
        status = "exterior_capacity_only_no_internal_hessian"

    gates = [
        {"gate":"H0_mode_count", "claim":"q_phi=dim H^0(S^2)=1", "result":1, "status":"derived", "reason":"S^2 is connected; only ell=0 gives 1/r decay."},
        {"gate":"exterior_capacity", "claim":"int |grad(phi R/r)|^2 = 4*pi*R*phi^2", "result_symbolic":str(ext["energy_integral"]), "result_at_R":float(ext["capacity"].subs(R,args.radius).evalf()), "status":"derived", "reason":"Direct exterior Laplace energy integral."},
        {"gate":"phase_Hessian_relation", "claim":"Lambda_phi=4*pi*R*K_cell", "result_symbolic":str(Lambda_from_K), "status":"derived", "reason":"Second derivative of A_far."},
        {"gate":"K_cell_value", "claim":"K_cell=E_eff/(8*pi*R) if Lambda_phi=E_eff/2", "result_symbolic":str(K_expr), "result_numeric":K_numeric, "status":status, "reason":"Requires independent interior one-cell Hessian."},
    ]
    pd.DataFrame(gates).to_csv(outdir/"phase_hessian_gates.csv", index=False)
    multipole_decay_table(args.lmax).to_csv(outdir/"multipole_decay_table.csv", index=False)

    expr_rows = [
        {"name":"u", "symbolic":str(ext["u"]), "latex":sp.latex(ext["u"])},
        {"name":"du_dr", "symbolic":str(ext["du_dr"]), "latex":sp.latex(ext["du_dr"])},
        {"name":"energy_integral", "symbolic":str(ext["energy_integral"]), "latex":sp.latex(ext["energy_integral"])},
        {"name":"capacity", "symbolic":str(ext["capacity"]), "latex":sp.latex(ext["capacity"])},
        {"name":"Lambda_from_K", "symbolic":str(Lambda_from_K), "latex":sp.latex(Lambda_from_K)},
        {"name":"K_from_Lambda", "symbolic":str(K_from_Lambda), "latex":sp.latex(K_from_Lambda)},
    ]
    pd.DataFrame(expr_rows).to_csv(outdir/"phase_hessian_symbolics.csv", index=False)

    report = ["# One-cell phase-Hessian gate", "", f"Radius R = {args.radius}", f"Lambda source = {args.lambda_source}", "", "The H^0(S^2) mode count and exterior capacity are derived. K_cell requires an independent interior Hessian Lambda_phi.", ""]
    for g in gates:
        report.append(f"## {g['gate']}")
        report += [f"- {k}: `{v}`" for k,v in g.items() if k != "gate"]
        report.append("")
    (outdir/"phase_hessian_report.md").write_text("\n".join(report), encoding="utf-8")

    tex = r"""\section{One-cell phase-Hessian gate}
For the exterior harmonic monopole with boundary value \(\phi\) at \(r=R\),
\[
  u(r)=\frac{\phi R}{r}.
\]
Therefore
\[
  \int_{r\ge R}|\nabla u|^2\,d^3x = 4\pi R\phi^2.
\]
With \(\mathcal A_{\rm far}=K_{\rm cell}\int |\nabla u|^2d^3x/2\),
\[
  \Lambda_\phi=4\pi R K_{\rm cell}.
\]
Only the \(\ell=0\) exterior harmonic contributes to the \(1/r\) field; hence
\(q_\phi=\dim H^0(S^2)=1\). If an independent cell calculation gives
\(\Lambda_\phi=E_{\rm eff}/2\), then
\[
  K_{\rm cell}=\frac{E_{\rm eff}}{8\pi R}.
\]
"""
    (outdir/"phase_hessian_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print(pd.DataFrame(gates).to_string(index=False))
    print(f"\nWrote {outdir}")

if __name__ == "__main__":
    main()
