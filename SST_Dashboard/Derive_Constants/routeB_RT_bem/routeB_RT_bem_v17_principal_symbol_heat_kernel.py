#!/usr/bin/env python3
r"""
routeB_RT_bem_v17_principal_symbol_heat_kernel.py
=================================================

BEMv17 Route-B audit: principal-symbol / heat-kernel coefficient derivation
for the BEMv16 normalizer

    N_RT = M_max L_cert^2.

BEMv16 established a conditional heat-kernel/DtN certificate.  BEMv17 sharpens
that into an explicit principal-symbol proof obligation:

    Find the order -2 residual symbol q_{-2}(x, xi) of the pair-subtracted
    R--T logarithmic boundary action.

If the first non-vanishing residual is order -2, then the local density scales
as L^{-2}; together with mode extensivity this gives

    DeltaF_phys = DeltaF_pair / (M_max L_cert^2).

No observed alpha is used or compared.

Outputs
-------
  bemv17_symbol_hierarchy.csv
  bemv17_heat_kernel_coefficients.csv
  bemv17_exponent_uniqueness.csv
  bemv17_proof_gap_register.csv
  bemv17_principal_symbol_certificate.csv
  bemv17_principal_symbol_appendix.tex
  bemv17_principal_symbol_report.md
  run_config_v17.json

Scale-role convention: r_c, R_horn, and a_tube
----------------------------------------------
Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
physical core radius into the BEM score.

When a physical radius is discussed, use

    r_c == R_horn

where R_horn is the horn-torus / return-flow circulation radius.  Do not
silently identify r_c with the local ideal-tube radius.  Use

    a_tube = R_horn / chi_h = r_c / chi_h
    ell_K_phys = 2 * a_tube * L_cert

The dimensionless Route-B normalizer remains

    N_RT = M_max * L_cert**2

while physical reconstruction uses

    L_phys**2 = 4 * a_tube**2 * L_cert**2
              = 4 * r_c**2 * L_cert**2 / chi_h**2

Only if chi_h is later made knot-dependent should a separate horn-effective
scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
certified dimensionless geometry mode.

"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def load_v16(v16_outdir: Path) -> Dict[str, Any]:
    certificate = read_csv(v16_outdir / "bemv16_heat_kernel_certificate.csv")
    link = read_csv(v16_outdir / "bemv16_v15_numeric_link.csv")
    link_map = {r.get("field", ""): r.get("value", "") for r in link}
    cert = certificate[0] if certificate else {}
    return {"certificate": cert, "link": link_map}


def symbol_hierarchy_rows(boundary_dim: int) -> List[Dict[str, Any]]:
    # For a d-dimensional boundary and a first-order DtN operator,
    # Weyl mode counting is M(Lambda) ~ C_d Vol(Sigma) Lambda^d.
    # The residual symbol order -r gives local scale L^{-r}.
    rows = []
    for r in [0, 1, 2, 3, 4]:
        rows.append({
            "residual_symbol_order": f"-{r}",
            "boundary_dimension_d": boundary_dim,
            "local_density_scale": f"L^(-{r})",
            "required_length_normalizer_power_b": r,
            "candidate_normalizer": f"M_max L_cert^{r}",
            "interpretation": (
                "order-0 residual; no length normalization"
                if r == 0 else
                "order-1 residual; one power of certified length"
                if r == 1 else
                "order-2 residual; BEMv16/BEMv17 target"
                if r == 2 else
                f"higher-order residual; length power {r}"
            ),
            "status": "TARGET" if r == 2 else "ALTERNATIVE_TO_FALSIFY",
        })
    return rows


def heat_kernel_rows(boundary_dim: int) -> List[Dict[str, Any]]:
    # Generic asymptotic slots, not numerical coefficients.
    return [
        {
            "slot": "principal Weyl count",
            "operator_order": 1,
            "boundary_dimension_d": boundary_dim,
            "asymptotic_form": "N(Lambda) ~ C_d Vol(Sigma) Lambda^d",
            "role": "Defines mode count M_max and supports mode-extensivity.",
            "normalizer_consequence": "one factor M_max",
            "status": "STANDARD_PSEUDODIFFERENTIAL_STRUCTURE",
        },
        {
            "slot": "log determinant pair subtraction",
            "operator_order": "log ratio of first-order maps",
            "boundary_dimension_d": boundary_dim,
            "asymptotic_form": "Tr log(Lambda_R Lambda_T^{-1}) with common leading symbols removed",
            "role": "Cancels shared leading area/cutoff terms.",
            "normalizer_consequence": "finite residual begins at lower symbol order",
            "status": "PROOF_OBLIGATION",
        },
        {
            "slot": "first nonzero residual coefficient",
            "operator_order": "-2 residual symbol",
            "boundary_dimension_d": boundary_dim,
            "asymptotic_form": "q_{-2}(x,xi) contributes length^{-2} density",
            "role": "Fixes L_cert^2 in denominator.",
            "normalizer_consequence": "length factor L_cert^2",
            "status": "TARGET_THEOREM_NOT_YET_DERIVED",
        },
        {
            "slot": "dimensionless intensive correction",
            "operator_order": "mode average of order -2 residual",
            "boundary_dimension_d": boundary_dim,
            "asymptotic_form": "DeltaF_pair/(M_max L_cert^2)",
            "role": "Produces alpha-blind finite correction for certified Route-B budget.",
            "normalizer_consequence": "N_RT = M_max L_cert^2",
            "status": "CONDITIONAL_RESULT",
        },
    ]


def exponent_uniqueness_rows() -> List[Dict[str, Any]]:
    # Monomial normalizer M^a L^b. Mode-extensivity -> a=1.
    # residual symbol order -2 -> b=2.
    rows = []
    candidates = [(0,0), (1,0), (1,1), (1,2), (1,3), (0.5,2), (2,2)]
    for a, b in candidates:
        mode_ok = abs(a-1) < 1e-12
        length_ok = abs(b-2) < 1e-12
        rows.append({
            "a_M_exponent": a,
            "b_L_exponent": b,
            "candidate": f"M_max^{a:g} L_cert^{b:g}",
            "mode_extensive_condition_a_eq_1": mode_ok,
            "order_minus_two_condition_b_eq_2": length_ok,
            "passes_bemv17_symbol_law": mode_ok and length_ok,
            "status": "UNIQUE_TARGET" if mode_ok and length_ok else "REJECTED_BY_SYMBOL_LAW",
        })
    return rows


def proof_gap_rows() -> List[Dict[str, Any]]:
    return [
        {
            "gap_id": "G17-1",
            "gap": "Construct the actual R--T boundary operators Lambda_R and Lambda_T as elliptic first-order pseudodifferential maps.",
            "needed_for": "DtN/Steklov order assumption",
            "current_status": "FORMAL_ASSUMPTION",
            "closure_test": "principal symbols sigma_1(Lambda_R), sigma_1(Lambda_T) exist and share the required leading-order class",
        },
        {
            "gap_id": "G17-2",
            "gap": "Show that pair subtraction cancels common order 0 / area / cutoff terms in Tr log(Lambda_R Lambda_T^{-1}).",
            "needed_for": "finite pair residual",
            "current_status": "PROOF_OBLIGATION",
            "closure_test": "heat-kernel coefficient cancellation table has zero residual through orders above -2",
        },
        {
            "gap_id": "G17-3",
            "gap": "Derive that the first nonzero residual symbol is q_{-2}, not q_0, q_{-1}, or q_{-3}.",
            "needed_for": "length exponent b=2",
            "current_status": "CENTRAL_OPEN_GATE",
            "closure_test": "symbol expansion of log ratio exhibits q_{-2} as first surviving term",
        },
        {
            "gap_id": "G17-4",
            "gap": "Relate certified length L_cert to the scale variable in the heat-kernel coefficient.",
            "needed_for": "certified-length branch",
            "current_status": "SUPPORTED_BY_BEMV11_BEMV12_BUT_NEEDS_THEOREM",
            "closure_test": "global rescaling of certified source-cell maps coefficient as L_cert^{-2}",
        },
        {
            "gap_id": "G17-5",
            "gap": "Extend beyond single-knot trefoil data to test length exponent b using multiple L_cert values.",
            "needed_for": "empirical identifiability of b",
            "current_status": "RECOMMENDED_NUMERICAL_CROSSCHECK",
            "closure_test": "multi-knot certified-length regression selects b=2 without observed alpha",
        },
    ]


def certificate_row(v16: Dict[str, Any]) -> Dict[str, Any]:
    cert = v16.get("certificate", {})
    link = v16.get("link", {})
    return {
        "normalizer": "M_max L_cert^2",
        "normalizer_code": "M_Lcert2",
        "bemv16_status": cert.get("proof_status", ""),
        "bemv17_status": "PRINCIPAL_SYMBOL_PROOF_OBLIGATION_CERTIFICATE",
        "symbol_target": "first surviving pair-subtracted residual q_{-2}",
        "mode_exponent_a": 1,
        "length_exponent_b": 2,
        "uses_observed_alpha": "no",
        "stageD_alpha_inv_mean": link.get("stageD_alpha_inv_mean", cert.get("stageD_alpha_inv_mean", "")),
        "stageD_alpha_inv_cv_abs": link.get("stageD_alpha_inv_cv_abs", cert.get("stageD_alpha_inv_cv_abs", "")),
        "stageCD_alpha_inv_mean": link.get("stageCD_alpha_inv_mean", ""),
        "stageCD_alpha_inv_cv_abs": link.get("stageCD_alpha_inv_cv_abs", ""),
        "next_gate": "BEMv18_MULTI_KNOT_LENGTH_EXPONENT_OR_SYMBOL_EXPANSION_Q_MINUS_2",
    }


def write_appendix(path: Path, v16: Dict[str, Any]) -> None:
    row = certificate_row(v16)
    tex = r"""
% BEMv17 appendix snippet
% Principal-symbol proof obligation for the Route-B certified normalizer.
% Alpha-blind: no observed fine-structure value is used.

\subsection{Principal-symbol route to the certified Route-B normalizer}

\paragraph{Status.}
This subsection refines the BEMv16 heat-kernel certificate into a
principal-symbol proof obligation.  The goal is not to fit a number, but to
derive the normalizer
\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}
\]
from the symbol expansion of the R--T boundary operator.

Let \(\Lambda_R\) and \(\Lambda_T\) be first-order elliptic
Dirichlet-to-Neumann/Steklov-type maps on the two-dimensional boundary
\(\Sigma_K\).  The generalized R--T spectrum is
\[
\Lambda_R u_j=\lambda_j\Lambda_T u_j .
\]
The pair-subtracted logarithmic action is
\[
\Delta F_{\rm pair}(K/0_1;M)
=
-\sum_{j=1}^{M}\log \lambda_j(K)
+
\sum_{j=1}^{M}\log \lambda_j(0_1).
\]

\paragraph{Symbol expansion.}
The proof target is to show that, after soft-sector removal and pair
subtraction, the logarithmic symbol has the schematic expansion
\[
\sigma\!\left[\log(\Lambda_R\Lambda_T^{-1})\right]
=
q_{-2}(x,\xi)
+
q_{-3}(x,\xi)
+\cdots ,
\]
with no surviving \(q_0\) or \(q_{-1}\) contribution in the finite residual.
The leading surviving density is then of order \(L^{-2}\).

\paragraph{Mode averaging.}
The cutoff \(M_{\max}\) counts retained boundary modes.  If the residual
action is extensive in the retained modes, then
\[
\Delta F_{\rm pair}
=
M_{\max}\,\bar q_{-2}
+
o(M_{\max}).
\]
Since \(q_{-2}\) carries scale weight \(L_{\rm cert}^{-2}\), the corresponding
dimensionless intensive correction is
\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

\begin{theorem}[Principal-symbol normalizer, conditional form]
Assume: (i) the R--T maps are first-order elliptic boundary maps; (ii) pair
subtraction cancels all residual terms above order \(-2\); (iii) the first
surviving residual is \(q_{-2}\); and (iv) the retained-mode truncation is
mode-extensive.  Then the unique separable monomial normalizer
\[
\mathcal N_{a,b}=M_{\max}^{a}L_{\rm cert}^{b}
\]
is obtained for
\[
a=1,\qquad b=2,
\]
namely
\[
\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}}.
\]
\end{theorem}

\paragraph{Numerical link.}
The BEMv14/BEMv15 evidence selects this normalizer across the supplied
multigrid data.  The Stage D alpha-blind subset gives
\[
\langle\alpha^{-1}_{\rm pred,blind}\rangle_D=__STAGED__,
\qquad
{\rm CV}_D=__STAGEDCV__.
\]
This numerical evidence supports the normalizer, but the theorem-level closure
still requires the explicit derivation of \(q_{-2}\).
""".strip()
    tex = tex.replace("__STAGED__", str(row.get("stageD_alpha_inv_mean", "")))
    tex = tex.replace("__STAGEDCV__", str(row.get("stageD_alpha_inv_cv_abs", "")))
    path.write_text(tex + "\n", encoding="utf-8")


def write_report(path: Path, v16: Dict[str, Any]) -> None:
    row = certificate_row(v16)
    lines = [
        "# BEMv17 principal-symbol / heat-kernel report",
        "",
        "This report is alpha-blind. It does not contain or compare against observed fine structure.",
        "",
        "## Target",
        "",
        "BEMv17 identifies the exact remaining proof obligation for",
        "",
        r"\[",
        r"\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.",
        r"\]",
        "",
        "The target is to derive the first surviving pair-subtracted residual symbol:",
        "",
        r"\[",
        r"q_{-2}(x,\xi).",
        r"\]",
        "",
        "If the residual starts at order -2, then the length exponent is fixed:",
        "",
        r"\[",
        r"b=2.",
        r"\]",
        "",
        "Mode extensivity fixes:",
        "",
        r"\[",
        r"a=1.",
        r"\]",
        "",
        "Together:",
        "",
        r"\[",
        r"\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}",
        r"\]",
        "",
        "## Certificate",
        "",
    ]
    for k, v in row.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += [
        "",
        "## Interpretation",
        "",
        "BEMv17 is stronger than BEMv16 because it localizes the remaining mathematical burden: derive cancellation of the order 0 and order -1 residual terms, and show that the first nonzero pair-subtracted symbol is order -2.",
        "",
        "## Next gate",
        "",
        r"\[",
        r"\boxed{\text{BEMv18: either multi-knot }b=2\text{ test or explicit }q_{-2}\text{ symbolic expansion.}}",
        r"\]",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v16-outdir", default="outputs_routeB_BEM_v16_heat_kernel")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v17_principal_symbol")
    ap.add_argument("--boundary-dim", type=int, default=2)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    v16 = load_v16(Path(args.v16_outdir))

    write_csv(outdir / "bemv17_symbol_hierarchy.csv", symbol_hierarchy_rows(args.boundary_dim))
    write_csv(outdir / "bemv17_heat_kernel_coefficients.csv", heat_kernel_rows(args.boundary_dim))
    write_csv(outdir / "bemv17_exponent_uniqueness.csv", exponent_uniqueness_rows())
    write_csv(outdir / "bemv17_proof_gap_register.csv", proof_gap_rows())
    write_csv(outdir / "bemv17_principal_symbol_certificate.csv", [certificate_row(v16)])
    write_appendix(outdir / "bemv17_principal_symbol_appendix.tex", v16)
    write_report(outdir / "bemv17_principal_symbol_report.md", v16)

    (outdir / "run_config_v17.json").write_text(json.dumps({"args": vars(args)}, indent=2), encoding="utf-8")

    cert = certificate_row(v16)
    print("=" * 78)
    print("Route B BEMv17 principal-symbol audit complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print("normalizer: M_max L_cert^2")
    print("target residual symbol: q_{-2}")
    print(f"Stage D mean: {cert.get('stageD_alpha_inv_mean','')}")
    print(f"Stage D CV: {cert.get('stageD_alpha_inv_cv_abs','')}")
    print("wrote: bemv17_symbol_hierarchy.csv, bemv17_heat_kernel_coefficients.csv,")
    print("       bemv17_exponent_uniqueness.csv, bemv17_proof_gap_register.csv,")
    print("       bemv17_principal_symbol_certificate.csv, bemv17_principal_symbol_appendix.tex,")
    print("       bemv17_principal_symbol_report.md")


if __name__ == "__main__":
    main()
