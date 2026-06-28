#!/usr/bin/env python3
"""
derive_pressure_self_duality.py

Reciprocity audit for the radius action
    A_chi = chi_R + N_p/chi_R.

Shows that in the leading scale-homogeneous reciprocal class
    A_chi = a chi_R + b N_p/chi_R,
self-duality under chi_R -> N_p/chi_R requires a=b. Then
    lambda_chi = (b/a) N_p,
    chi_R* = sqrt((b/a) N_p).
For N_p=4 and a=b: lambda_chi=4 and chi_R*=2.

Epistemic status: this proves the result inside the leading reciprocal,
self-dual inner/outer pressure class. It does not prove that full primitive
field equations forbid higher-order or nonreciprocal terms; those are audited
as sensitivity variants.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import sympy as sp


def compute(Np: sp.Expr, ratio: sp.Expr, include_log=False, include_quad=False):
    chi, a, b, c_log, c_quad = sp.symbols("chi_R a b c_log c_quad", positive=True, real=True)
    A = a*chi + b*Np/chi
    if include_log:
        A += c_log*sp.log(chi)
    if include_quad:
        A += c_quad*chi**2
    A_dual = sp.simplify(A.subs(chi, Np/chi))
    A_diff = sp.simplify(A_dual - A)

    A_min = chi + ratio*Np/chi
    dA = sp.diff(A_min, chi)
    crit = sp.solve(sp.Eq(dA,0), chi)
    chi_star = sp.simplify(crit[0]) if crit else sp.nan
    lambda_chi = sp.simplify(ratio*Np)
    return {
        "A_general":A,
        "A_dual":A_dual,
        "A_dual_minus_A":A_diff,
        "A_min_selected":A_min,
        "dA_min":dA,
        "chi_star":chi_star,
        "lambda_chi":lambda_chi,
        "self_dual_exact_for_minimal_class": sp.simplify(ratio-1)==0,
        "matches_lambda_4": sp.simplify(lambda_chi-4)==0,
        "matches_chi_2": sp.simplify(chi_star-2)==0,
    }


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--N-p", default="4", help="Pressure sector count.")
    ap.add_argument("--b-over-a", default="1", help="Inner/outer ratio b/a.")
    ap.add_argument("--include-log", action="store_true")
    ap.add_argument("--include-quad", action="store_true")
    ap.add_argument("--outdir", default="outputs_pressure_self_duality")
    args=ap.parse_args()
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    Np=sp.sympify(args.N_p); ratio=sp.sympify(args.b_over_a)
    res=compute(Np, ratio, args.include_log, args.include_quad)
    gates=[
        {"gate":"reciprocal_action_class", "claim":"A_chi=a chi_R + b N_p/chi_R", "result":str(res["A_general"]), "status":"model_class_defined", "reason":"Outer extension scales as chi_R; inner crowding scales as N_p/chi_R."},
        {"gate":"self_duality", "claim":"A(N_p/chi_R)=A(chi_R) requires a=b in the minimal class", "dual_minus_original":str(res["A_dual_minus_A"]), "b_over_a":str(ratio), "status":"self_dual" if res["self_dual_exact_for_minimal_class"] else "not_self_dual_sensitivity_variant", "reason":"Equality under inner/outer exchange fixes equal normalization."},
        {"gate":"radius_stationarity", "claim":"chi_R*=sqrt((b/a)N_p)", "result":str(res["chi_star"]), "status":"chi_R_2" if res["matches_chi_2"] else "shifted_chi_R", "reason":"Stationarity of A_chi."},
        {"gate":"lambda_chi", "claim":"lambda_chi=(b/a)N_p", "result":str(res["lambda_chi"]), "status":"lambda_chi_4" if res["matches_lambda_4"] else "shifted_lambda_chi", "reason":"In A=chi+lambda/chi, lambda=(b/a)N_p."},
    ]
    pd.DataFrame(gates).to_csv(outdir/"pressure_self_duality_gates.csv", index=False)
    expr_rows=[{"name":k, "symbolic":str(v), "latex":sp.latex(v) if isinstance(v, sp.Basic) else str(v)} for k,v in res.items()]
    pd.DataFrame(expr_rows).to_csv(outdir/"pressure_self_duality_symbolics.csv", index=False)

    sens=[]
    for rr in [sp.Rational(4,5), sp.Rational(1), sp.Rational(21,20), sp.Rational(5,4)]:
        r=compute(Np, rr)
        sens.append({"b_over_a":str(rr), "lambda_chi":str(r["lambda_chi"]), "chi_star":str(r["chi_star"]), "matches_chi_2":bool(r["matches_chi_2"])})
    pd.DataFrame(sens).to_csv(outdir/"pressure_self_duality_sensitivity.csv", index=False)

    report=["# Pressure self-duality gate", "", f"N_p = {Np}", f"b/a = {ratio}", "", f"A_min = {res['A_min_selected']}", f"chi_star = {res['chi_star']}", f"lambda_chi = {res['lambda_chi']}", "", "Status: " + ("derived_in_self_dual_minimal_class" if res["matches_chi_2"] and res["matches_lambda_4"] else "sensitivity_variant"), "", "This proves chi_R=2 only inside the self-dual leading reciprocal class. Higher-order terms must be shown subleading or forbidden by the primitive equations."]
    (outdir/"pressure_self_duality_report.md").write_text("\n".join(report), encoding="utf-8")

    tex=r"""\section{Pressure self-duality gate}
At leading scale order the outer cell-extension cost is proportional to
\(\chi_R\), while the inner crowding/compliance cost is reciprocal and
proportional to the number of pressure sectors:
\[
  A_\chi=a\chi_R+b\frac{N_p}{\chi_R}.
\]
The duality transformation exchanging inner and outer scales is
\[
  \chi_R\mapsto\frac{N_p}{\chi_R}.
\]
Demanding \(A_\chi(N_p/\chi_R)=A_\chi(\chi_R)\) for the minimal reciprocal
class fixes \(a=b\). Therefore
\[
  A_\chi=\chi_R+\frac{N_p}{\chi_R}.
\]
Stationarity gives
\[
  \frac{dA_\chi}{d\chi_R}=1-\frac{N_p}{\chi_R^2}=0,
  \qquad
  \chi_R=\sqrt{N_p}.
\]
For \(N_p=4\),
\[
  \chi_R=2,
  \qquad
  \lambda_\chi=N_p=4.
\]
This is derived inside the self-dual leading reciprocal pressure class. A full
primitive-equation derivation must show that nonreciprocal or higher-order
terms are absent or subleading.
"""
    (outdir/"pressure_self_duality_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print(pd.DataFrame(gates).to_string(index=False))
    print(f"\nWrote {outdir}")

if __name__ == "__main__":
    main()
