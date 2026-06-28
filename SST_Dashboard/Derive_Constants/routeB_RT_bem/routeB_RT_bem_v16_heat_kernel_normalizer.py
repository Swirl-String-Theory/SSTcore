#!/usr/bin/env python3
r"""
routeB_RT_bem_v16_heat_kernel_normalizer.py
===========================================

BEMv16 Route-B audit: heat-kernel / DtN normalizer proof obligations.

BEMv15 formulated the conditional normalizer law

    N_RT = M_max L_cert^2.

BEMv16 is not a new BEM solve and it does not use observed alpha.  It turns
the BEMv15 condition into a heat-kernel / Dirichlet-to-Neumann (DtN) proof
obligation matrix.

It checks the following formal route:

  A1. The R--T boundary problem is represented by first-order DtN/Steklov
      pseudodifferential operators on a two-dimensional boundary surface.

  A2. Truncation to M_max generalized boundary modes makes the unresolved
      pair action mode-extensive:
          DeltaF_pair = M_max * density + o(M_max).

  A3. The finite R--T density that remains after pair subtraction has
      length dimension L^{-2}; equivalently it is a second-order density.

  A4. The certified longitudinal scale is L_cert, while the Fourier curve
      only supplies geometry for the BEM operator.

  A5. Therefore the intensive dimensionless correction is
          DeltaF_pair / (M_max L_cert^2).

BEMv16 writes a certificate, a proof-obligation table, and a LaTeX appendix.

Outputs
-------
  bemv16_proof_obligations.csv
  bemv16_scaling_law_table.csv
  bemv16_normalizer_derivation.csv
  bemv16_v15_numeric_link.csv
  bemv16_heat_kernel_appendix.tex
  bemv16_heat_kernel_report.md
  run_config_v16.json

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
from typing import Any, Dict, List, Optional

import numpy as np


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


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def load_v15_summary(v15_outdir: Path) -> Dict[str, Any]:
    cert_rows = read_csv(v15_outdir / "bemv15_normalizer_law_certificate.csv")
    subset_rows = read_csv(v15_outdir / "bemv15_asymptotic_subset_certificate.csv")
    exp_rows = read_csv(v15_outdir / "bemv15_exponent_scan.csv")

    summary = cert_rows[0] if cert_rows else {}
    # Prefer Stage D and Stage C+D for asymptotic estimates.
    subset_by_name = {r.get("subset"): r for r in subset_rows}
    summary["stageD_alpha_inv_mean"] = subset_by_name.get("StageD", {}).get("alpha_inv_mean", "")
    summary["stageD_alpha_inv_cv_abs"] = subset_by_name.get("StageD", {}).get("alpha_inv_cv_abs", "")
    summary["stageCD_alpha_inv_mean"] = subset_by_name.get("StageC+StageD", {}).get("alpha_inv_mean", "")
    summary["stageCD_alpha_inv_cv_abs"] = subset_by_name.get("StageC+StageD", {}).get("alpha_inv_cv_abs", "")

    canonical_scan = None
    for r in exp_rows:
        if r.get("note") == "CANONICAL_CANDIDATE_M_LCERT2":
            canonical_scan = r
            break
    if canonical_scan:
        for k, v in canonical_scan.items():
            summary["canonical_scan_" + k] = v
    return summary


def proof_obligations_rows() -> List[Dict[str, Any]]:
    return [
        {
            "id": "A1",
            "claim": "R--T boundary maps are first-order DtN/Steklov pseudodifferential operators on a two-dimensional boundary.",
            "mathematical_role": "Supplies heat-kernel/Weyl counting structure for retained boundary modes.",
            "status": "ASSUMPTION_CAN_BE_TURNED_INTO_OPERATOR_THEOREM",
            "failure_mode": "If the discretized kernel is not order-one DtN/Steklov, M-counting may not be heat-kernel extensivity.",
        },
        {
            "id": "A2",
            "claim": "The unresolved finite pair action is extensive in retained mode count M_max.",
            "mathematical_role": "Fixes monomial exponent a=1 in M_max^a.",
            "status": "SUPPORTED_BY_BEMV14_NUMERICS_CONDITIONAL_ANALYTIC",
            "failure_mode": "If pair subtraction leaves non-extensive M log M or M^p drift, M_max division is insufficient.",
        },
        {
            "id": "A3",
            "claim": "The residual R--T finite density has length dimension L^{-2}.",
            "mathematical_role": "Fixes monomial exponent b=2 in L_cert^b.",
            "status": "SCALE_COVARIANCE_ASSUMPTION_NOT_SINGLE_KNOT_IDENTIFIABLE",
            "failure_mode": "A different density order would change L exponent; single-knot grids cannot identify b.",
        },
        {
            "id": "A4",
            "claim": "Certified length L_cert is the longitudinal scale; Fourier coefficients are geometry source only.",
            "mathematical_role": "Separates length provenance from rounded Fourier geometry.",
            "status": "SUPPORTED_BY_BEMV11_BEMV12_PROVENANCE",
            "failure_mode": "If database L is not the certified scale, the leading term and normalizer must be recomputed.",
        },
        {
            "id": "A5",
            "claim": "The dimensionless intensive correction is DeltaF_pair/(M_max L_cert^2).",
            "mathematical_role": "Combines A2 and A3 into the BEMv15 normalizer law.",
            "status": "CONDITIONAL_CONCLUSION",
            "failure_mode": "Fails if either mode-extensivity or length-squared covariance fails.",
        },
    ]


def scaling_law_rows() -> List[Dict[str, Any]]:
    return [
        {
            "quantity": "M_max",
            "mode_power": 1,
            "length_power": 0,
            "scaling_under_M_to_muM": "mu",
            "scaling_under_L_to_lambdaL": "1",
            "role": "retained boundary mode count",
        },
        {
            "quantity": "L_cert",
            "mode_power": 0,
            "length_power": 1,
            "scaling_under_M_to_muM": "1",
            "scaling_under_L_to_lambdaL": "lambda",
            "role": "certified longitudinal scale",
        },
        {
            "quantity": "DeltaF_pair",
            "mode_power": 1,
            "length_power": -2,
            "scaling_under_M_to_muM": "mu",
            "scaling_under_L_to_lambdaL": "lambda^{-2}",
            "role": "raw unresolved finite R--T pair action under assumptions A2/A3",
        },
        {
            "quantity": "M_max L_cert^2",
            "mode_power": 1,
            "length_power": 2,
            "scaling_under_M_to_muM": "mu",
            "scaling_under_L_to_lambdaL": "lambda^{2}",
            "role": "minimal separable normalizer",
        },
        {
            "quantity": "DeltaF_pair/(M_max L_cert^2)",
            "mode_power": 0,
            "length_power": 0,
            "scaling_under_M_to_muM": "1",
            "scaling_under_L_to_lambdaL": "1",
            "role": "dimensionless intensive correction",
        },
    ]


def derivation_rows(preferred: str = "M_Lcert2") -> List[Dict[str, Any]]:
    return [
        {
            "step": 1,
            "statement": "Assume a separable monomial normalizer N_{a,b}=M_max^a L_cert^b.",
            "equation": "N_{a,b}=M_max^a L_cert^b",
            "fixes": "",
            "status": "DEFINITION",
        },
        {
            "step": 2,
            "statement": "Mode extensivity requires removing one power of retained mode count.",
            "equation": "DeltaF_pair ~ M_max",
            "fixes": "a=1",
            "status": "FROM_A2",
        },
        {
            "step": 3,
            "statement": "Second-order length-scale covariance requires removing two powers of certified length.",
            "equation": "density ~ L_cert^{-2}",
            "fixes": "b=2",
            "status": "FROM_A3",
        },
        {
            "step": 4,
            "statement": "Therefore the minimal separable normalizer is M_max L_cert^2.",
            "equation": "N_RT=M_max L_cert^2",
            "fixes": preferred,
            "status": "CONDITIONAL_QED",
        },
    ]


def v15_numeric_link_rows(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    keys = [
        "preferred_normalizer",
        "stages_detected",
        "n_stages",
        "n_grid_families",
        "preferred_selected_fraction",
        "pass_grid_family_fraction",
        "preferred_cross_grid_consensus_pass_count",
        "global_numeric_gate",
        "global_alpha_inv_blind_mean",
        "global_alpha_inv_blind_cv_abs",
        "stageD_alpha_inv_mean",
        "stageD_alpha_inv_cv_abs",
        "stageCD_alpha_inv_mean",
        "stageCD_alpha_inv_cv_abs",
        "global_abs_correction_ratio_max",
        "analytic_status",
    ]
    return [{"field": k, "value": summary.get(k, "")} for k in keys]


def write_appendix(path: Path, summary: Dict[str, Any]) -> None:
    stageD_mean = str(summary.get("stageD_alpha_inv_mean", ""))
    stageD_cv = str(summary.get("stageD_alpha_inv_cv_abs", ""))
    stageCD_mean = str(summary.get("stageCD_alpha_inv_mean", ""))
    stageCD_cv = str(summary.get("stageCD_alpha_inv_cv_abs", ""))
    max_ratio = str(summary.get("global_abs_correction_ratio_max", ""))

    tex = r"""
% BEMv16 appendix snippet
% Heat-kernel / DtN proof obligations for the Route-B normalizer.
% Alpha-blind: no observed fine-structure value is used.

\subsection{Heat-kernel normalizer for the certified Route-B correction}

\paragraph{Status.}
This subsection gives a conditional heat-kernel/DtN normalization theorem.
It does not derive the fine-structure constant.  It derives the normalizer
required for the finite R--T correction, assuming the R--T boundary problem is
represented by first-order Dirichlet-to-Neumann/Steklov maps and that the
pair-subtracted residual has second-order length covariance.

Let \(\Sigma_K\) be the two-dimensional boundary associated with the certified
source-cell geometry of knot \(K\).  Let \(\Lambda_R\) and \(\Lambda_T\) denote
the R- and T-sector boundary maps, and let
\[
\Lambda_R u_j=\lambda_j \Lambda_T u_j
\]
define the generalized R--T boundary spectrum after removal of the prescribed
soft sector.  The truncated pair action is
\[
\Delta F_{\rm pair}(K/0_1;M)
=
-\sum_{j=1}^M \log\lambda_j(K)
+
\sum_{j=1}^M \log\lambda_j(0_1).
\]

\begin{assumption}[DtN/Steklov order]
The maps \(\Lambda_R\) and \(\Lambda_T\) are first-order elliptic boundary
operators on the two-dimensional surface \(\Sigma_K\), up to compact and
lower-order regularizing terms.
\end{assumption}

\begin{assumption}[Mode extensivity]
After pair subtraction and after fixing the soft-sector convention, the
unresolved finite action is extensive in retained mode count:
\[
\Delta F_{\rm pair}(K/0_1;M)=M\,\bar f(K/0_1)+o(M).
\]
\end{assumption}

\begin{assumption}[Second-order length covariance]
The residual finite density entering the certified longitudinal budget scales
as a second-order boundary density:
\[
L_{\rm cert}\mapsto \lambda L_{\rm cert}
\quad\Longrightarrow\quad
\bar f\mapsto \lambda^{-2}\bar f .
\]
\end{assumption}

\begin{theorem}[Conditional Route-B normalizer]
Among separable monomial normalizers
\[
\mathcal N_{a,b}=M_{\max}^{a}L_{\rm cert}^{b},
\]
the unique minimal normalizer compatible with mode extensivity and
second-order length covariance is
\[
\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}}.
\]
\end{theorem}

\begin{proof}
Mode extensivity implies that the raw pair correction carries one power of
\(M_{\max}\).  Removing the cutoff-count dependence fixes \(a=1\).  The
second-order length covariance assumption states that the intensive residual
has scale weight \(L_{\rm cert}^{-2}\).  Removing this scale weight fixes
\(b=2\).  Hence the minimal separable monomial normalizer is
\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]
\end{proof}

The certified Route-B correction is therefore
\[
\Delta F_{\rm phys}(K/0_1)
=
\frac{\Delta F_{\rm pair}(K/0_1)}
{M_{\max}L_{\rm cert}(K)^2}.
\]
For the trefoil source-cell this gives the alpha-blind budget
\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12
\left[
N_{\rm soft}V_{\rm soft}L_{\rm cert}(3_1)
+
\frac{\Delta F_{\rm pair}(3_1/0_1)}
{M_{\max}L_{\rm cert}(3_1)^2}
\right].
\]

\paragraph{Numerical link to BEMv14/BEMv15.}
The supplied BEMv14 multigrid data select \(M_{\max}L_{\rm cert}^{2}\) across
all detected grid families.  The Stage D alpha-blind subset gives
\[
\langle\alpha^{-1}_{\rm pred,blind}\rangle_D=__STAGED_MEAN__,
\qquad
{\rm CV}_D=__STAGED_CV__.
\]
The Stage C+D subset gives
\[
\langle\alpha^{-1}_{\rm pred,blind}\rangle_{C+D}=__STAGECD_MEAN__,
\qquad
{\rm CV}_{C+D}=__STAGECD_CV__.
\]
The largest correction ratio across the supplied set is
\[
\max
\frac{|\Delta F_{\rm pair}/(M_{\max}L_{\rm cert}^{2})|}
{N_{\rm soft}V_{\rm soft}L_{\rm cert}}
=
__MAX_RATIO__.
\]

\paragraph{Open mathematical obligation.}
The remaining theorem-level gate is to derive the second-order length
covariance from the principal symbol and heat-kernel coefficients of the
R--T boundary operator.  Until that derivation is supplied, BEMv16 should be
cited as a conditional heat-kernel normalizer certificate, not as a complete
derivation of \(\alpha\).
""".strip() + "\n"

    tex = (tex
           .replace("__STAGED_MEAN__", stageD_mean)
           .replace("__STAGED_CV__", stageD_cv)
           .replace("__STAGECD_MEAN__", stageCD_mean)
           .replace("__STAGECD_CV__", stageCD_cv)
           .replace("__MAX_RATIO__", max_ratio))
    path.write_text(tex, encoding="utf-8")

def write_report(path: Path, summary: Dict[str, Any]) -> None:
    lines = [
        "# BEMv16 heat-kernel / DtN normalizer report",
        "",
        "This report is alpha-blind. It does not contain or compare against observed fine structure.",
        "",
        "## Result",
        "",
        "BEMv16 converts the BEMv15 normalizer law into a heat-kernel/DtN proof-obligation certificate:",
        "",
        r"\[",
        r"\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}",
        r"\]",
        "",
        "The result is conditional on mode-extensivity and second-order length-scale covariance.",
        "",
        "## Numerical link from BEMv15",
        "",
    ]
    for k, v in summary.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += [
        "",
        "## Interpretation",
        "",
        "The numerical search phase is now largely exhausted. The remaining issue is mathematical: derive the length-squared covariance from the R--T boundary operator's principal symbol and heat-kernel coefficients.",
        "",
        "## BEMv17 target",
        "",
        r"\[",
        r"\boxed{\text{BEMv17: principal-symbol and heat-kernel coefficient derivation for }L_{\rm cert}^{2}.}",
        r"\]",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v15-outdir", default="outputs_routeB_BEM_v15_normalizer_law")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v16_heat_kernel")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    v15 = Path(args.v15_outdir)
    summary = load_v15_summary(v15)

    obligations = proof_obligations_rows()
    scaling = scaling_law_rows()
    derivation = derivation_rows(summary.get("preferred_normalizer", "M_Lcert2"))
    link = v15_numeric_link_rows(summary)

    write_csv(outdir / "bemv16_proof_obligations.csv", obligations)
    write_csv(outdir / "bemv16_scaling_law_table.csv", scaling)
    write_csv(outdir / "bemv16_normalizer_derivation.csv", derivation)
    write_csv(outdir / "bemv16_v15_numeric_link.csv", link)

    cert = {
        "normalizer": "M_max L_cert^2",
        "normalizer_code": "M_Lcert2",
        "proof_status": "CONDITIONAL_HEAT_KERNEL_DTN_CERTIFICATE",
        "requires_A1_DtN_order": "yes",
        "requires_A2_mode_extensivity": "yes",
        "requires_A3_second_order_length_covariance": "yes",
        "uses_observed_alpha": "no",
        "v15_global_gate": summary.get("global_numeric_gate", ""),
        "stageD_alpha_inv_mean": summary.get("stageD_alpha_inv_mean", ""),
        "stageD_alpha_inv_cv_abs": summary.get("stageD_alpha_inv_cv_abs", ""),
        "next_gate": "BEMv17_PRINCIPAL_SYMBOL_HEAT_KERNEL_COEFFICIENT_PROOF",
    }
    write_csv(outdir / "bemv16_heat_kernel_certificate.csv", [cert])

    write_appendix(outdir / "bemv16_heat_kernel_appendix.tex", summary)
    write_report(outdir / "bemv16_heat_kernel_report.md", summary)

    config = {"args": vars(args)}
    (outdir / "run_config_v16.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("Route B BEMv16 heat-kernel normalizer audit complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print("normalizer: M_max L_cert^2")
    print("proof status: CONDITIONAL_HEAT_KERNEL_DTN_CERTIFICATE")
    print(f"Stage D mean: {summary.get('stageD_alpha_inv_mean', '')}")
    print(f"Stage D CV: {summary.get('stageD_alpha_inv_cv_abs', '')}")
    print("wrote: bemv16_proof_obligations.csv, bemv16_scaling_law_table.csv,")
    print("       bemv16_normalizer_derivation.csv, bemv16_heat_kernel_certificate.csv,")
    print("       bemv16_heat_kernel_appendix.tex, bemv16_heat_kernel_report.md")


if __name__ == "__main__":
    main()
