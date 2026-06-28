#!/usr/bin/env python3
r"""
routeB_RT_bem_v15_normalizer_law.py
===================================

BEMv15 Route-B audit: normalizer law certificate.

BEMv14 multigrid results show that the certified-length budget repeatedly
selects

    N_q = M_max L_cert^2.

BEMv15 does not run a new BEM operator. It ingests Stage A/B/C/D BEMv14
multigrid outputs, certifies the empirical cross-grid normalizer consensus,
and writes a conditional analytic certificate for

    N_RT = M_max L_cert^2.

No observed alpha is used or compared.

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
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


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


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def extract_inputs(inputs: List[str], work: Path) -> List[Path]:
    roots: List[Path] = []
    for item in inputs:
        p = Path(item)
        if not p.exists():
            raise FileNotFoundError(p)
        if p.is_file() and p.suffix.lower() == ".zip":
            target = work / safe_name(p.stem)
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p, "r") as z:
                z.extractall(target)
            roots.append(target)
        elif p.is_dir():
            roots.append(p)
        else:
            raise ValueError(f"unsupported input {p}")
    return roots


def stage_label_from_path(p: Path) -> str:
    for part in reversed(p.parts):
        if "stageA" in part:
            return "StageA"
        if "stageB" in part:
            return "StageB"
        if "stageC" in part:
            return "StageC"
        if "stageD" in part:
            return "StageD"
    return p.parent.name


def discover_stage_dirs(roots: List[Path]) -> List[Path]:
    dirs = []
    for r in roots:
        for p in r.rglob("multigrid_consensus_summary.csv"):
            dirs.append(p.parent)
    out: List[Path] = []
    seen = set()
    for d in dirs:
        key = str(d.resolve())
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def load_all(stage_dirs: List[Path]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    stage_rows: List[Dict[str, Any]] = []
    consensus_rows: List[Dict[str, Any]] = []
    budget_rows: List[Dict[str, Any]] = []

    for d in stage_dirs:
        stage = stage_label_from_path(d)

        for r in read_csv(d / "multigrid_selected_normalizers.csv"):
            rr = dict(r)
            rr["stage"] = stage
            rr["stage_dir"] = str(d)
            stage_rows.append(rr)

        for r in read_csv(d / "multigrid_consensus_summary.csv"):
            rr = dict(r)
            rr["stage"] = stage
            rr["stage_dir"] = str(d)
            consensus_rows.append(rr)

        for r in read_csv(d / "multigrid_budget_aggregate.csv"):
            rr = dict(r)
            rr["stage"] = stage
            rr["stage_dir"] = str(d)
            L = as_float(rr.get("L_cert_target"))
            den = as_float(rr.get("normalizer_denominator"))
            rr["Mmax_inferred_from_denominator"] = den/(L*L) if math.isfinite(L) and L != 0 and math.isfinite(den) else ""
            budget_rows.append(rr)

    return stage_rows, consensus_rows, budget_rows


def summarize_global(stage_rows: List[Dict[str, Any]], consensus_rows: List[Dict[str, Any]], budget_rows: List[Dict[str, Any]], preferred: str) -> Dict[str, Any]:
    selected = [r.get("selected_normalizer", "") for r in stage_rows if r.get("selected_normalizer", "")]
    selected_counter = Counter(selected)
    stages = sorted(set(r.get("stage", "") for r in stage_rows))
    grid_families = len(stage_rows)

    preferred_selected = selected_counter.get(preferred, 0)
    pass_grid_families = sum(1 for r in stage_rows if str(r.get("stability_gate", "")).startswith("PASS"))
    consensus_pass = sum(1 for r in consensus_rows if r.get("normalizer") == preferred and r.get("cross_grid_gate") == "PASS_CROSS_GRID_CONSENSUS")

    vals = np.asarray([as_float(r.get("alpha_inv_pred_blind_v13")) for r in budget_rows], dtype=float)
    vals = vals[np.isfinite(vals)]
    ratios = np.asarray([as_float(r.get("correction_to_leading_ratio")) for r in budget_rows], dtype=float)
    ratios = ratios[np.isfinite(ratios)]

    mean = float(np.mean(vals)) if len(vals) else float("nan")
    std = float(np.std(vals, ddof=1)) if len(vals) > 1 else (0.0 if len(vals) == 1 else float("nan"))
    span = float(np.max(vals)-np.min(vals)) if len(vals) else float("nan")
    cv = abs(std/mean) if math.isfinite(mean) and abs(mean) > 1e-300 else float("nan")
    max_ratio = float(np.max(np.abs(ratios))) if len(ratios) else float("nan")

    global_gate = (
        "PASS_G14_NUMERIC_SUPPORT_FOR_M_LCERT2"
        if grid_families > 0
        and preferred_selected == grid_families
        and pass_grid_families == grid_families
        and consensus_pass >= len(stages)
        else "FAIL_OR_INCOMPLETE_G14_NUMERIC_SUPPORT"
    )

    return {
        "preferred_normalizer": preferred,
        "stages_detected": ",".join(stages),
        "n_stages": len(stages),
        "n_grid_families": grid_families,
        "preferred_selected_count": preferred_selected,
        "preferred_selected_fraction": preferred_selected/grid_families if grid_families else float("nan"),
        "pass_grid_family_count": pass_grid_families,
        "pass_grid_family_fraction": pass_grid_families/grid_families if grid_families else float("nan"),
        "preferred_cross_grid_consensus_pass_count": consensus_pass,
        "global_alpha_inv_blind_mean": mean,
        "global_alpha_inv_blind_std": std,
        "global_alpha_inv_blind_span": span,
        "global_alpha_inv_blind_cv_abs": cv,
        "global_abs_correction_ratio_max": max_ratio,
        "global_numeric_gate": global_gate,
        "analytic_status": "CONDITIONAL_LAW_UNDER_H1_MODE_EXTENSIVITY_AND_H2_SCALE_COVARIANCE",
    }


def exponent_scan(budget_rows: List[Dict[str, Any]], a_values: List[float], b_values: List[float], ratio_threshold: float, cv_threshold: float) -> List[Dict[str, Any]]:
    pts = []
    for r in budget_rows:
        L = as_float(r.get("L_cert_target"))
        M = as_float(r.get("Mmax_inferred_from_denominator"))
        dF = as_float(r.get("DeltaF_pair_raw"))
        leading_half = as_float(r.get("leading_half_alpha_inv_cert"))
        if all(math.isfinite(x) for x in [L, M, dF, leading_half]) and L > 0 and M > 0:
            pts.append((L, M, dF, leading_half))
    rows = []
    for a in a_values:
        for b in b_values:
            vals, ratios = [], []
            for L, M, dF, leading_half in pts:
                N = (M**a) * (L**b)
                dphys = dF / N
                vals.append(leading_half + 0.5*dphys)
                ratios.append(abs(dphys)/(2.0*abs(leading_half)))
            arr = np.asarray(vals, dtype=float)
            rat = np.asarray(ratios, dtype=float)
            if len(arr) == 0:
                continue
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
            span = float(np.max(arr)-np.min(arr))
            cv = abs(std/mean) if mean != 0 else float("nan")
            max_ratio = float(np.max(rat)) if len(rat) else float("nan")
            gate = "PASS_NUMERIC_STABILITY" if cv <= cv_threshold and max_ratio <= ratio_threshold else "FAIL_NUMERIC_STABILITY"
            note = "CANONICAL_CANDIDATE_M_LCERT2" if abs(a-1.0)<1e-12 and abs(b-2.0)<1e-12 else ""
            rows.append({
                "a_M_exponent": a,
                "b_L_exponent": b,
                "normalizer_formula": f"M^{a:g} L^{b:g}",
                "n_points": len(arr),
                "alpha_inv_mean": mean,
                "alpha_inv_std": std,
                "alpha_inv_span": span,
                "alpha_inv_cv_abs": cv,
                "abs_correction_ratio_max": max_ratio,
                "numeric_gate": gate,
                "note": note,
            })
    return rows


def write_appendix(path: Path, summary: Dict[str, Any]) -> None:
    tex = f"""
% BEMv15 appendix snippet
% Conditional normalizer law for Route-B certified-length budget.
% This snippet is alpha-blind: it contains no observed fine-structure input.

\\subsection{{Conditional normalizer law for the certified Route-B correction}}

\\paragraph{{Status.}}
The result in this subsection is a conditional normalization certificate, not a
first-principles derivation of the fine-structure constant. It identifies the
minimal separable monomial normalizer compatible with the numerical BEMv14
evidence and with two structural assumptions on the truncated R--T spectral action.

Let
\\[
S_M(K/0_1)
=
-\\sum_{{j=1}}^M \\log\\lambda_j(K)
+
\\sum_{{j=1}}^M \\log\\lambda_j(0_1)
\\]
denote the finite pair-subtracted R--T spectral action after the BEM
discretization has produced \\(M=M_{{\\max}}\\) retained modes. Let
\\(L_{{\\rm cert}}(K)\\) denote the certified length from the ideal-knot database,
used only for the longitudinal scale.

\\begin{{assumption}}[Mode extensivity]
For fixed geometry and fixed cutoff prescription, the unresolved finite
pair-action is extensive in the number of retained spectral degrees of freedom:
\\[
\\Delta F_{{\\rm pair}}(K/0_1;M)
=
M\\,\\bar f(K/0_1)+o(M).
\\]
Hence an intensive correction must contain a factor \\(M^{-1}\\).
\\end{{assumption}}

\\begin{{assumption}}[Length-scale covariance]
The finite R--T correction entering the certified longitudinal budget is a
second-order boundary density under global rescaling of the certified
longitudinal scale:
\\[
L_{{\\rm cert}}\\mapsto \\lambda L_{{\\rm cert}},
\\qquad
\\bar f\\mapsto \\lambda^{{-2}}\\bar f .
\\]
Equivalently, the corresponding dimensionless intensive correction is obtained
by dividing the raw pair-action by \\(M L_{{\\rm cert}}^2\\).
\\end{{assumption}}

\\begin{{lemma}}[Separable monomial normalizer]
Consider separable monomial normalizers of the form
\\[
\\mathcal N_{{a,b}}=M_{{\\max}}^a L_{{\\rm cert}}^b .
\\]
Mode extensivity fixes \\(a=1\\). Length-scale covariance fixes \\(b=2\\). Thus
the minimal separable normalizer compatible with the two assumptions is
\\[
\\boxed{{\\mathcal N_{{\\rm RT}}=M_{{\\max}}L_{{\\rm cert}}^2}}.
\\]
\\end{{lemma}}

The certified Route-B budget then becomes
\\[
\\alpha^{{-1}}_{{\\rm pred,blind}}
=
\\frac12
\\left[
N_{{\\rm soft}}V_{{\\rm soft}}L_{{\\rm cert}}(3_1)
+
\\frac{{\\Delta F_{{\\rm pair}}(3_1/0_1)}}
{{M_{{\\max}}L_{{\\rm cert}}(3_1)^2}}
\\right].
\\]
All quantities on the right are internal to the Route-B audit: no observed
fine-structure value is used.

\\paragraph{{Numerical certificate from BEMv14.}}
Across the supplied BEMv14 multigrid stages the selected normalizer is
\\[
\\mathcal N_{{\\rm RT}}=M_{{\\max}}L_{{\\rm cert}}^2 .
\\]
The aggregated alpha-blind budget statistics are
\\[
\\langle \\alpha^{{-1}}_{{\\rm pred,blind}}\\rangle
=
{summary['global_alpha_inv_blind_mean']:.12f},
\\qquad
\\sigma
=
{summary['global_alpha_inv_blind_std']:.12e},
\\qquad
{{\\rm CV}}
=
{summary['global_alpha_inv_blind_cv_abs']:.12e}.
\\]
The largest normalized correction ratio in the supplied runs is
\\[
\\max
\\frac{{|\\Delta F_{{\\rm pair}}/(M_{{\\max}}L_{{\\rm cert}}^2)|}}
{{N_{{\\rm soft}}V_{{\\rm soft}}L_{{\\rm cert}}}}
=
{summary['global_abs_correction_ratio_max']:.12e}.
\\]

\\paragraph{{Remaining open gate.}}
The exponent \\(b=2\\) is not identifiable from single-knot data alone because
\\(L_{{\\rm cert}}(3_1)\\) is fixed across the present grid. Its use is therefore
a scale-covariance assumption, not a purely empirical fit. A stronger closure
requires either a multi-knot certified-length test or an analytic heat-kernel
derivation of the length-squared density.
""".strip() + "\n"
    path.write_text(tex, encoding="utf-8")


def write_report(path: Path, summary: Dict[str, Any], consensus_rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# BEMv15 normalizer law report",
        "",
        "This report is alpha-blind: it does not contain or compare against observed fine structure.",
        "",
        "## Core claim",
        "",
        "BEMv15 promotes the repeatedly selected BEMv14 normalizer to a conditional normalizer law:",
        "",
        r"\[",
        r"\boxed{\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}",
        r"\]",
        "",
        "The claim is conditional: it follows from mode-extensivity plus length-scale covariance. It is not yet a full heat-kernel theorem.",
        "",
        "## Global numerical certificate",
        "",
    ]
    for k, v in summary.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Stage consensus", ""]
    for r in consensus_rows:
        lines.append(f"- `{r.get('stage')}`: `{r.get('normalizer')}` selected by `{r.get('n_grid_families_selected')}` grid families; gate `{r.get('cross_grid_gate')}`; aggregate CV `{r.get('aggregate_cv_abs')}`")
    lines += [
        "",
        "## Interpretation",
        "",
        "The supplied Stage A/B/C/D data give strong numerical support for \(M_{\max}L_{\rm cert}^{2}\) as the Route-B certified-length normalizer.",
        "",
        "The remaining theoretical task is no longer another blind numerical search. It is an analytic derivation of mode extensivity and the \(L_{\rm cert}^{2}\) scale-covariance factor from the R--T boundary operator.",
        "",
        "## Next gate",
        "",
        r"\[",
        r"\boxed{\text{BEMv16: heat-kernel / DtN proof of } \mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.}",
        r"\]",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="comma-separated BEMv14 stage zips or output folders")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v15_normalizer_law")
    ap.add_argument("--preferred-normalizer", default="M_Lcert2")
    ap.add_argument("--ratio-threshold", type=float, default=0.05)
    ap.add_argument("--cv-threshold", type=float, default=0.01)
    ap.add_argument("--scan-a", default="0,0.5,1,1.5,2")
    ap.add_argument("--scan-b", default="0,1,2,3,4")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    work = outdir / "_extracted_inputs"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    inputs = [s.strip() for s in args.inputs.split(",") if s.strip()]
    roots = extract_inputs(inputs, work)
    stage_dirs = discover_stage_dirs(roots)
    stage_rows, consensus_rows, budget_rows = load_all(stage_dirs)

    write_csv(outdir / "bemv15_stage_summary.csv", stage_rows)
    write_csv(outdir / "bemv15_consensus_summary.csv", consensus_rows)
    write_csv(outdir / "bemv15_budget_points.csv", budget_rows)

    summary = summarize_global(stage_rows, consensus_rows, budget_rows, args.preferred_normalizer)
    write_csv(outdir / "bemv15_normalizer_law_certificate.csv", [summary])

    a_values = [float(x.strip()) for x in args.scan_a.split(",") if x.strip()]
    b_values = [float(x.strip()) for x in args.scan_b.split(",") if x.strip()]
    scan = exponent_scan(budget_rows, a_values, b_values, args.ratio_threshold, args.cv_threshold)
    write_csv(outdir / "bemv15_exponent_scan.csv", scan)

    write_appendix(outdir / "bemv15_normalizer_law_appendix.tex", summary)
    write_report(outdir / "bemv15_normalizer_law_report.md", summary, consensus_rows)

    config = {"args": vars(args), "inputs": inputs, "stage_dirs": [str(d) for d in stage_dirs]}
    (outdir / "run_config_v15.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    print("="*78)
    print("Route B BEMv15 normalizer-law audit complete")
    print("="*78)
    print(f"outdir: {outdir}")
    print(f"stage dirs detected: {len(stage_dirs)}")
    print(f"preferred normalizer: {summary['preferred_normalizer']}")
    print(f"selected fraction: {summary['preferred_selected_fraction']}")
    print(f"global gate: {summary['global_numeric_gate']}")
    print(f"global mean: {summary['global_alpha_inv_blind_mean']}")
    print(f"global CV: {summary['global_alpha_inv_blind_cv_abs']}")


if __name__ == "__main__":
    main()
