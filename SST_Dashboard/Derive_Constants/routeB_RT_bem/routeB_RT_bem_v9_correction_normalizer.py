#!/usr/bin/env python3
r"""
routeB_RT_bem_v9_correction_normalizer.py
=========================================

BEMv9 Route-B audit: alpha-blind finite-correction normalizer scan.

BEMv8 restored the leading longitudinal scale:

  alpha_inv_lead = 1/2 * N_soft V_soft L_long(3_1)

but the direct finite pair correction DeltaF_pair was still much too large in
raw form.

BEMv9 does not fit alpha.  It scans alpha-blind normalization maps

  DeltaF_phys = DeltaF_pair / N_q(K, ref)

where N_q is built only from internal mesh/geometric/spectral quantities, e.g.

  M_max, sqrt(M_max), L, L^2, L^3, N_soft V_soft L, ...

Then it reports

  alpha_inv_pred_blind_v9(q)
    = 1/2 * [N_soft V_soft L_long + DeltaF_phys(q)].

This is a falsifier: a candidate normalizer is only plausible if it is
stable and leaves the finite correction subleading.

Outputs
-------
  finite_correction_normalizers.csv
  alpha_budget_v9_candidates.csv
  correction_gate_report.md
  blind_alpha_prediction_v9.md

Input
-----
BEMv9 can reuse an existing BEMv8 folder via --from-bemv8-outdir or run BEMv8
as a substep.

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
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
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


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


# ---------------------------------------------------------------------------
# Optional BEMv8 execution
# ---------------------------------------------------------------------------

def run_bemv8(v8_script: Path, args, outdir: Path) -> None:
    cmd = [
        sys.executable, str(v8_script),
        "--ideal", str(args.ideal),
        "--ideal-xml-knot-ids", args.ideal_xml_knot_ids,
        "--outdir", str(outdir),
        "--target", args.target,
        "--reference", args.reference,
        "--n-center", str(args.n_center),
        "--n-theta", str(args.n_theta),
        "--n-sphere", str(args.n_sphere),
        "--tube-fraction", str(args.tube_fraction),
        "--outer-factor", str(args.outer_factor),
        "--mu-mode", args.mu_mode,
        "--mu-value", str(args.mu_value),
        "--boundary-subspace", args.boundary_subspace,
        "--fit-min-M", str(args.fit_min_M),
        "--counterterm-fit-min-M", str(args.counterterm_fit_min_M),
        "--fit-tail-frac", str(args.fit_tail_frac),
        "--counterterm-tail-frac", str(args.counterterm_tail_frac),
        "--fit-models", args.fit_models,
        "--counterterm-models", args.counterterm_models,
        "--soft-index-count", str(args.soft_index_count),
        "--soft-volume-mode", args.soft_volume_mode,
        "--soft-volume-value", str(args.soft_volume_value),
        "--length-samples", str(args.length_samples),
        "--length-source", args.length_source,
        "--length-fit-model", args.length_fit_model,
        "--length-coeff", args.length_coeff,
        "--length-fit-min-M", str(args.length_fit_min_M),
        "--length-fit-tail-frac", str(args.length_fit_tail_frac),
        "--pair-fit-model", args.pair_fit_model,
        "--pair-fit-min-M", str(args.pair_fit_min_M),
        "--pair-fit-tail-frac", str(args.pair_fit_tail_frac),
    ]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.subrun_timeout)
    (outdir / "bemv8_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (outdir / "bemv8_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"BEMv8 subrun failed with return code {proc.returncode}; see {outdir}/bemv8_stderr.txt")


# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------

def get_target_row(rows: List[Dict[str, str]], target: str, reference: str = "") -> Dict[str, str]:
    for r in rows:
        if r.get("target") == target or r.get("knot") == target:
            if not reference or r.get("reference", reference) == reference:
                return r
    if len(rows) == 1:
        return rows[0]
    raise ValueError(f"target row not found target={target!r} reference={reference!r}")


def compute_denominator(name: str, ctx: Dict[str, float]) -> Tuple[float, str]:
    L = ctx["L"]
    M = ctx["Mmax"]
    leading_full = ctx["leading_full"]
    leading_half = ctx["leading_half"]
    NsoftV = ctx["NsoftV"]
    NsoftVL = ctx["NsoftVL"]
    sqrtM = math.sqrt(M) if M > 0 else float("nan")

    table = {
        "raw": (1.0, "no normalization"),
        "Mmax": (M, "divide by pair-fit M_max"),
        "sqrtM": (sqrtM, "divide by sqrt(M_max)"),
        "L": (L, "divide by restored longitudinal length"),
        "L2": (L * L, "divide by restored longitudinal length squared"),
        "L3": (L * L * L, "divide by restored longitudinal length cubed"),
        "NsoftV": (NsoftV, "divide by N_soft V_soft"),
        "NsoftV_L": (NsoftVL, "divide by N_soft V_soft L"),
        "leading_full": (leading_full, "divide by full leading length term N_soft V_soft L"),
        "leading_half": (leading_half, "divide by half leading length term"),
        "M_L": (M * L, "divide by M_max times length"),
        "sqrtM_L": (sqrtM * L, "divide by sqrt(M_max) times length"),
        "M_L2": (M * L * L, "divide by M_max times length squared"),
    }
    if name not in table:
        raise ValueError(f"unknown normalizer {name!r}")
    return table[name]


def build_v9_outputs(outdir: Path, bemv8_dir: Path, args) -> Dict[str, Any]:
    budget_rows = read_csv_rows(bemv8_dir / "alpha_component_budget_v8.csv")
    pair_rows = read_csv_rows(bemv8_dir / "pair_subtracted_correction.csv")
    length_rows = read_csv_rows(bemv8_dir / "spectral_length_estimate_phys.csv")
    geom_rows = read_csv_rows(bemv8_dir / "geometric_length_audit.csv")

    if not budget_rows:
        raise RuntimeError(f"missing {bemv8_dir}/alpha_component_budget_v8.csv")
    if not pair_rows:
        raise RuntimeError(f"missing {bemv8_dir}/pair_subtracted_correction.csv")

    b = get_target_row(budget_rows, args.target, args.reference)
    p = get_target_row(pair_rows, args.target, args.reference)

    target = b.get("target", args.target)
    reference = b.get("reference", args.reference)

    L = as_float(b.get("L_long_target"))
    NsoftV = as_float(b.get("S_soft_per_unit_length"))
    leading_half = as_float(b.get("leading_length_term_half_NsoftVsoftL"))
    leading_full = 2.0 * leading_half if math.isfinite(leading_half) else NsoftV * L
    DeltaF_pair = as_float(b.get("DeltaF_pair_target_reference", p.get("DeltaF_pair")))
    Mmax = as_float(p.get("M_max", p.get("max_common_modes", "nan")))
    if not math.isfinite(Mmax):
        Mmax = as_float(p.get("max_common_modes"))

    ctx = {
        "L": L,
        "Mmax": Mmax,
        "NsoftV": NsoftV,
        "NsoftVL": NsoftV * L,
        "leading_full": leading_full,
        "leading_half": leading_half,
    }

    norm_names = [x.strip() for x in args.normalizers.split(",") if x.strip()]
    normalizer_rows: List[Dict[str, Any]] = []
    candidate_rows: List[Dict[str, Any]] = []

    for norm in norm_names:
        denom, desc = compute_denominator(norm, ctx)
        if not math.isfinite(denom) or abs(denom) < 1e-300:
            Delta_phys = float("nan")
            status = "FAIL_BAD_DENOMINATOR"
        else:
            Delta_phys = DeltaF_pair / denom
            status = "PASS_NUMERIC"

        half_corr = 0.5 * Delta_phys if math.isfinite(Delta_phys) else float("nan")
        alpha_pred = 0.5 * (leading_full + Delta_phys) if math.isfinite(Delta_phys) else float("nan")
        ratio = abs(Delta_phys) / abs(leading_full) if math.isfinite(Delta_phys) and abs(leading_full) > 0 else float("nan")
        gate = (
            "PASS_SUBLEADING_CORRECTION"
            if math.isfinite(ratio) and ratio <= args.subleading_threshold
            else "FAIL_NOT_SUBLEADING"
        )
        if status != "PASS_NUMERIC":
            gate = status

        normalizer_rows.append({
            "normalizer": norm,
            "description": desc,
            "denominator": denom,
            "DeltaF_pair_raw": DeltaF_pair,
            "DeltaF_phys_normalized": Delta_phys,
            "correction_to_leading_ratio": ratio,
            "gate": gate,
        })
        candidate_rows.append({
            "target": target,
            "reference": reference,
            "normalizer": norm,
            "length_source": b.get("length_source", ""),
            "L_long_target": L,
            "NsoftV": NsoftV,
            "leading_full_inside_bracket": leading_full,
            "leading_half_alpha_inv": leading_half,
            "DeltaF_pair_raw": DeltaF_pair,
            "normalizer_denominator": denom,
            "DeltaF_phys_normalized": Delta_phys,
            "finite_correction_half": half_corr,
            "alpha_inv_pred_blind_v9": alpha_pred,
            "correction_to_leading_ratio": ratio,
            "subleading_threshold": args.subleading_threshold,
            "gate": gate,
            "status": "ALPHA_BLIND_NORMALIZER_CANDIDATE_NOT_CODATA_COMPARISON",
        })

    write_csv(outdir / "finite_correction_normalizers.csv", normalizer_rows)
    write_csv(outdir / "alpha_budget_v9_candidates.csv", candidate_rows)

    # Select a non-raw passing candidate with smallest ratio, else smallest ratio overall.
    candidates = [r for r in candidate_rows if math.isfinite(as_float(r["alpha_inv_pred_blind_v9"]))]
    passers = [r for r in candidates if r["gate"] == "PASS_SUBLEADING_CORRECTION" and r["normalizer"] != "raw"]
    if passers:
        selected = sorted(passers, key=lambda r: abs(as_float(r["correction_to_leading_ratio"])))[0]
    elif candidates:
        selected = sorted(candidates, key=lambda r: abs(as_float(r["correction_to_leading_ratio"], 1e99)))[0]
    else:
        selected = {"gate": "NO_NUMERIC_CANDIDATE"}

    return {
        "bemv8_budget": b,
        "pair_row": p,
        "normalizer_rows": normalizer_rows,
        "candidate_rows": candidate_rows,
        "selected": selected,
        "target": target,
        "reference": reference,
        "geom_rows": geom_rows,
        "length_rows": length_rows,
    }


def write_reports(outdir: Path, result: Dict[str, Any], args, input_source: str) -> None:
    selected = result["selected"]

    lines: List[str] = []
    lines.append("# BEMv9 finite-correction normalizer gate report")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("This report is alpha-blind. It does not contain or compare against observed alpha.")
    lines.append("")
    lines.append("BEMv9 scans internal normalizers")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"\Delta F_{\rm phys}^{(q)}=\Delta F_{\rm pair}/\mathcal N_q.")
    lines.append(r"\]")
    lines.append("")
    lines.append("A candidate passes the first normalizer gate only if the normalized correction is subleading relative to")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"N_{\rm soft}V_{\rm soft}L_{\rm long}.")
    lines.append(r"\]")
    lines.append("")
    lines.append("## Selected diagnostic candidate")
    lines.append("")
    for k, v in selected.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("A passing normalizer is not a derivation. It only means the finite correction has been reduced to a subleading scale without using observed alpha.")
    lines.append("The next gate is convergence: the same normalizer must remain stable under mesh/tube/outer-boundary refinement.")
    lines.append("")
    lines.append(f"Input/source: `{input_source}`")
    (outdir / "correction_gate_report.md").write_text("\n".join(lines), encoding="utf-8")

    lines2: List[str] = []
    lines2.append("# Blind BEMv9 alpha-budget candidates")
    lines2.append("")
    lines2.append("The table `alpha_budget_v9_candidates.csv` contains all candidate budgets.")
    lines2.append("")
    lines2.append("The provisional selected diagnostic candidate is:")
    lines2.append("")
    for k in [
        "normalizer", "L_long_target", "leading_half_alpha_inv",
        "DeltaF_pair_raw", "normalizer_denominator", "DeltaF_phys_normalized",
        "finite_correction_half", "alpha_inv_pred_blind_v9",
        "correction_to_leading_ratio", "gate"
    ]:
        if k in selected:
            lines2.append(f"- `{k}`: `{selected[k]}`")
    lines2.append("")
    lines2.append("No observed alpha was used.")
    (outdir / "blind_alpha_prediction_v9.md").write_text("\n".join(lines2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v9")
    ap.add_argument("--v8-script", default=None)
    ap.add_argument("--from-bemv8-outdir", default="", help="reuse existing BEMv8 output instead of running BEMv8")

    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1")
    ap.add_argument("--target", default="3_1")
    ap.add_argument("--reference", default="0_1")

    # Pass-through BEMv8/BEMv5 parameters.
    ap.add_argument("--n-center", type=int, default=32)
    ap.add_argument("--n-theta", type=int, default=6)
    ap.add_argument("--n-sphere", type=int, default=144)
    ap.add_argument("--tube-fraction", type=float, default=0.30)
    ap.add_argument("--outer-factor", type=float, default=2.6)
    ap.add_argument("--mu-mode", choices=["inverse_tube_radius", "inverse_outer_radius", "fixed", "zero"], default="inverse_outer_radius")
    ap.add_argument("--mu-value", type=float, default=1.0)
    ap.add_argument("--boundary-subspace", choices=["all", "tube", "sphere"], default="all")
    ap.add_argument("--keep-constant", action="store_true")
    ap.add_argument("--no-auto-add-unknot", action="store_true")
    ap.add_argument("--max-raw-modes", type=int, default=0)

    ap.add_argument("--fit-min-M", type=int, default=4)
    ap.add_argument("--counterterm-fit-min-M", type=int, default=4)
    ap.add_argument("--fit-tail-frac", type=float, default=0.75)
    ap.add_argument("--counterterm-tail-frac", type=float, default=0.75)
    ap.add_argument("--fit-models", default="sqrt,sqrt+inv,sqrt+inv+threehalf")
    ap.add_argument("--counterterm-models", default="hk,hk+inv_sqrt,hk+inv_sqrt+inv")

    ap.add_argument("--soft-index-count", type=int, default=4)
    ap.add_argument("--soft-volume-mode", choices=["none", "unit_ball", "sphere_surface", "numeric"], default="unit_ball")
    ap.add_argument("--soft-volume-value", type=float, default=0.0)

    ap.add_argument("--length-samples", type=int, default=12000)
    ap.add_argument("--length-source", choices=["geometric_raw", "spectral_norm", "spectral_norm_rescaled_to_geom_ref"], default="geometric_raw")
    ap.add_argument("--length-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--length-coeff", default="A_M")
    ap.add_argument("--length-fit-min-M", type=int, default=4)
    ap.add_argument("--length-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--pair-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--pair-fit-min-M", type=int, default=4)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)

    # BEMv9 new controls.
    ap.add_argument("--normalizers", default="raw,Mmax,sqrtM,L,L2,L3,NsoftV,NsoftV_L,leading_full,leading_half,M_L,sqrtM_L,M_L2")
    ap.add_argument("--subleading-threshold", type=float, default=0.05)
    ap.add_argument("--subrun-timeout", type=int, default=300)

    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.from_bemv8_outdir:
        bemv8_dir = Path(args.from_bemv8_outdir)
        if not bemv8_dir.exists():
            raise FileNotFoundError(bemv8_dir)
        input_source = f"existing BEMv8 outdir={bemv8_dir}"
    else:
        bemv8_dir = outdir / "bemv8_base"
        bemv8_dir.mkdir(parents=True, exist_ok=True)
        v8_script = Path(args.v8_script) if args.v8_script else Path(__file__).with_name("routeB_RT_bem_v8_pair_length_budget.py")
        if not v8_script.exists():
            fallback = Path("/mnt/data/routeB_RT_bem_v8_pair_length_budget.py")
            if fallback.exists():
                v8_script = fallback
            else:
                raise FileNotFoundError(f"BEMv8 script not found: {v8_script}")
        run_bemv8(v8_script, args, bemv8_dir)
        input_source = f"BEMv8 subrun={bemv8_dir}"

    result = build_v9_outputs(outdir, bemv8_dir, args)
    write_reports(outdir, result, args, input_source)

    config = {"args": vars(args), "input_source": input_source, "bemv8_dir": str(bemv8_dir)}
    (outdir / "run_config_v9.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    selected = result["selected"]
    print("=" * 78)
    print("Route B BEMv9 correction-normalizer audit complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"source: {input_source}")
    print(f"selected normalizer: {selected.get('normalizer')}")
    print(f"gate: {selected.get('gate')}")
    print(f"alpha_inv_pred_blind_v9: {selected.get('alpha_inv_pred_blind_v9')}")
    print("wrote: finite_correction_normalizers.csv, alpha_budget_v9_candidates.csv, correction_gate_report.md, blind_alpha_prediction_v9.md")


if __name__ == "__main__":
    main()
