#!/usr/bin/env python3
"""
derive_gp_shell_deficit.py

Controlled symbolic audit of the GP/NLS shell-deficit gate.

Computes the coefficient in
    E_shell = E_0 [1 - sigma eta_K^2 + O(eta_K^3)]
from
  1. spherical volume Jacobian second variation: sigma_vol=3,
  2. isotropic transverse GP/NLS gradient projection:
     sigma_perp = w_perp <sin^2 theta> = (2/3) w_perp.

For the unweighted isotropic transverse shell model w_perp=1:
    sigma = 3 + 2/3 = 11/3.
With chi_R=2 and eta_K=1/(2 chi_R L_K)=1/(4 L_K):
    sigma eta_K^2 = 11/(48 L_K^2).

Epistemic status: this proves 11/48 under the unweighted isotropic GP/NLS
shell reduction. It does not prove by itself that the full microscopic GP core
profile forces w_perp=1; it makes that gate explicit and reports sensitivity.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import sympy as sp


def compute(w_perp: sp.Expr, chi_R: sp.Expr):
    eta, theta, L = sp.symbols("eta theta L_K", positive=True, real=True)
    jac = (1 - eta) ** 3
    jac_expanded = sp.expand(jac)
    sigma_vol = sp.Abs(jac_expanded.coeff(eta, 2))
    avg_sin2 = sp.simplify(
        sp.integrate(sp.sin(theta)**2 * sp.sin(theta), (theta,0,sp.pi)) /
        sp.integrate(sp.sin(theta), (theta,0,sp.pi))
    )
    projector_trace_average = sp.Rational(2,3)
    sigma_perp = sp.simplify(w_perp * avg_sin2)
    sigma_total = sp.simplify(sigma_vol + sigma_perp)
    eta_K = sp.simplify(1/(2*chi_R*L))
    c2 = sp.simplify(sigma_total/(4*chi_R**2))
    shell_factor = sp.simplify(1 - c2/L**2)
    return {
        "jacobian": jac_expanded,
        "sigma_volume": sigma_vol,
        "sin2_average": avg_sin2,
        "projector_trace_average": projector_trace_average,
        "w_perp": w_perp,
        "sigma_perp": sigma_perp,
        "sigma_total": sigma_total,
        "chi_R": chi_R,
        "eta_K": eta_K,
        "c2": c2,
        "shell_factor": shell_factor,
        "target_sigma": sp.Rational(11,3),
        "target_c2": sp.Rational(11,48),
        "sigma_matches_11_over_3": sp.simplify(sigma_total-sp.Rational(11,3)) == 0,
        "c2_matches_11_over_48": sp.simplify(c2-sp.Rational(11,48)) == 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--w-perp", default="1", help="Transverse shell weight. Default 1.")
    ap.add_argument("--chi-R", default="2", help="Cell radius ratio. Default 2.")
    ap.add_argument("--L-K", type=float, default=16.371637, help="Numeric ropelength for reporting.")
    ap.add_argument("--outdir", default="outputs_gp_shell_deficit")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    w_perp = sp.sympify(args.w_perp)
    chi_R = sp.sympify(args.chi_R)
    res = compute(w_perp, chi_R)

    Lval = args.L_K
    c2_num = float(sp.N(res["c2"]))
    shell_factor_num = 1.0 - c2_num/(Lval*Lval)

    gates = [
        {"gate":"spherical_volume_second_variation", "claim":"sigma_vol=3", "result":str(res["sigma_volume"]), "status":"derived", "reason":"(1-eta)^3 has eta^2 coefficient 3."},
        {"gate":"transverse_NLS_projection", "claim":"<sin^2 theta>_S2=2/3", "result":str(res["sin2_average"]), "status":"derived", "reason":"Isotropic angular average / transverse projector trace."},
        {"gate":"unweighted_GP_shell_deficit", "claim":"sigma=3+(2/3)w_perp", "result":str(res["sigma_total"]), "status":"derived_in_unweighted_shell_model" if res["sigma_matches_11_over_3"] else "sensitivity_variant_not_11_over_3", "reason":"11/3 requires w_perp=1."},
        {"gate":"finite_shell_coefficient", "claim":"c2=sigma/(4 chi_R^2)", "result":str(res["c2"]), "numeric":c2_num, "status":"matches_11_over_48" if res["c2_matches_11_over_48"] else "does_not_match_11_over_48", "reason":"With chi_R=2 and sigma=11/3, c2=11/48."},
    ]
    pd.DataFrame(gates).to_csv(outdir/"gp_shell_deficit_gates.csv", index=False)

    rows = []
    for k,v in res.items():
        rows.append({"name":k, "symbolic":str(v), "latex":sp.latex(v) if isinstance(v, sp.Basic) else str(v)})
    rows.append({"name":"shell_factor_numeric_at_LK", "symbolic":str(shell_factor_num), "latex":str(shell_factor_num)})
    pd.DataFrame(rows).to_csv(outdir/"gp_shell_deficit_symbolics.csv", index=False)

    sens=[]
    for w in [sp.Rational(0), sp.Rational(1,2), sp.Rational(1), sp.Rational(11,10), sp.Rational(3,2)]:
        r=compute(w, chi_R)
        sens.append({"w_perp":str(w), "sigma":str(r["sigma_total"]), "c2":str(r["c2"]), "shell_factor_at_LK":float(1-float(sp.N(r["c2"]))/(Lval*Lval)), "matches_11_over_48":bool(r["c2_matches_11_over_48"])})
    pd.DataFrame(sens).to_csv(outdir/"gp_shell_deficit_sensitivity.csv", index=False)

    report=["# GP/NLS shell deficit gate", "", f"w_perp = {w_perp}", f"chi_R = {chi_R}", f"L_K = {Lval}", "", f"sigma = {res['sigma_total']}", f"c2 = {res['c2']}", f"shell factor at L_K = {shell_factor_num:.12g}", "", "Status: " + ("derived_in_unweighted_shell_model" if res["c2_matches_11_over_48"] else "sensitivity_variant_not_11_over_48"), "", "This script does not prove that the microscopic GP core profile forces w_perp=1; it proves the coefficient under the unweighted isotropic shell reduction and reports sensitivity."]
    (outdir/"gp_shell_deficit_report.md").write_text("\n".join(report), encoding="utf-8")

    tex = r"""\section{GP/NLS shell-deficit gate}
The spherical shell Jacobian gives
\[
  (1-\eta)^3=1-3\eta+3\eta^2+O(\eta^3),
\]
hence \(\sigma_{\rm vol}=3\). The isotropic transverse GP/NLS gradient
projection gives
\[
  \langle \sin^2\theta\rangle_{S^2}
  =
  \frac{\int_0^\pi \sin^2\theta\,\sin\theta\,d\theta}
       {\int_0^\pi \sin\theta\,d\theta}
  =
  \frac23.
\]
With unweighted transverse response \(w_\perp=1\),
\[
  \sigma=3+\frac23=\frac{11}{3}.
\]
Since \(\eta_K=1/(2\chi_R\mathcal L_K)\) and \(\chi_R=2\),
\[
  \sigma\eta_K^2
  =
  \frac{11}{3}\frac{1}{16\mathcal L_K^2}
  =
  \frac{11}{48\mathcal L_K^2}.
\]
This is derived within the unweighted isotropic GP/NLS shell reduction. A full
microscopic proof must still derive \(w_\perp=1\) from the GP core-profile
expansion rather than imposing it.
"""
    (outdir/"gp_shell_deficit_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print(pd.DataFrame(gates).to_string(index=False))
    print(f"\nWrote {outdir}")

if __name__ == "__main__":
    main()
