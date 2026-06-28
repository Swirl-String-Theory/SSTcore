#!/usr/bin/env python3
r"""
routeB_RT_bem_v10_normalizer_convergence.py
===========================================

BEMv10 Route-B audit: convergence grid for BEMv9 finite-correction normalizers.

BEMv9 scans alpha-blind normalizers

    DeltaF_phys(q) = DeltaF_pair / N_q

and writes alpha_budget_v9_candidates.csv.

BEMv10 either:
  A. runs BEMv9 over a mesh/tube/outer-boundary grid, or
  B. reuses existing BEMv9 output directories via --from-bemv9-outdirs.

It then tests whether a normalizer is stable over the grid. No observed alpha
is used or compared.

Outputs
-------
  normalizer_convergence_grid.csv
  normalizer_stability_summary.csv
  alpha_budget_v10_convergence.csv
  blind_alpha_convergence_v10.md
  run_config_v10.json
  runs/<run_id>/... when BEMv9 is launched internally.

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
import itertools
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def parse_list_int(s: str) -> List[int]:
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_float(s: str) -> List[float]:
    return [float(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_str(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
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


def make_grid(args) -> List[Dict[str, Any]]:
    if args.grid_json:
        return json.loads(Path(args.grid_json).read_text(encoding="utf-8"))

    n_centers = parse_list_int(args.n_center_list)
    n_thetas = parse_list_int(args.n_theta_list)
    n_spheres = parse_list_int(args.n_sphere_list)
    tube_fracs = parse_list_float(args.tube_fraction_list)
    outer_factors = parse_list_float(args.outer_factor_list)

    if args.grid_mode == "paired":
        L = max(len(n_centers), len(n_thetas), len(n_spheres), len(tube_fracs), len(outer_factors))
        def pick(xs, i): return xs[min(i, len(xs)-1)]
        return [
            {
                "n_center": pick(n_centers, i),
                "n_theta": pick(n_thetas, i),
                "n_sphere": pick(n_spheres, i),
                "tube_fraction": pick(tube_fracs, i),
                "outer_factor": pick(outer_factors, i),
            }
            for i in range(L)
        ]

    return [
        {
            "n_center": nc,
            "n_theta": nt,
            "n_sphere": ns,
            "tube_fraction": tf,
            "outer_factor": of,
        }
        for nc, nt, ns, tf, of in itertools.product(n_centers, n_thetas, n_spheres, tube_fracs, outer_factors)
    ]


def run_bemv9(v9_script: Path, args, cfg: Dict[str, Any], run_dir: Path) -> Tuple[int, str, str]:
    cmd = [
        sys.executable, str(v9_script),
        "--ideal", str(args.ideal),
        "--outdir", str(run_dir),
        "--ideal-xml-knot-ids", args.ideal_xml_knot_ids,
        "--target", args.target,
        "--reference", args.reference,
        "--n-center", str(cfg["n_center"]),
        "--n-theta", str(cfg["n_theta"]),
        "--n-sphere", str(cfg["n_sphere"]),
        "--tube-fraction", str(cfg["tube_fraction"]),
        "--outer-factor", str(cfg["outer_factor"]),
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
        "--normalizers", args.normalizers,
        "--subleading-threshold", str(args.subleading_threshold),
        "--subrun-timeout", str(args.subrun_timeout),
    ]
    if args.v8_script:
        cmd += ["--v8-script", str(args.v8_script)]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.grid_run_timeout)
    (run_dir / "bemv9_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (run_dir / "bemv9_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def collect_from_bemv9_dir(run_id: str, run_dir: Path, cfg: Dict[str, Any], returncode: int = 0) -> List[Dict[str, Any]]:
    cand = read_csv_rows(run_dir / "alpha_budget_v9_candidates.csv")
    rows: List[Dict[str, Any]] = []
    if not cand:
        return [{
            "run_id": run_id,
            "returncode": returncode,
            "normalizer": "",
            "gate": "NO_CANDIDATE_ROWS",
            "run_dir": str(run_dir),
            **cfg,
        }]
    for r in cand:
        rows.append({
            "run_id": run_id,
            "returncode": returncode,
            "run_dir": str(run_dir),
            "h": (1.0 / float(cfg["n_center"])) if cfg.get("n_center") else "",
            "Rinv": (1.0 / float(cfg["outer_factor"])) if cfg.get("outer_factor") else "",
            **cfg,
            **r,
        })
    return rows


def build_grid_rows(outdir: Path, args) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if args.from_bemv9_outdirs:
        for i, item in enumerate(parse_list_str(args.from_bemv9_outdirs), start=1):
            run_dir = Path(item)
            cfg = {
                "n_center": "",
                "n_theta": "",
                "n_sphere": "",
                "tube_fraction": "",
                "outer_factor": "",
            }
            cfg_path = run_dir / "run_config_v9.json"
            if cfg_path.exists():
                try:
                    cfg_json = json.loads(cfg_path.read_text(encoding="utf-8"))
                    a = cfg_json.get("args", {})
                    for k in cfg:
                        cfg[k] = a.get(k, "")
                except Exception:
                    pass
            run_id = f"reuse{i:03d}_{safe_id(run_dir.name)}"
            rows.extend(collect_from_bemv9_dir(run_id, run_dir, cfg, returncode=0))
        write_csv(outdir / "normalizer_convergence_grid.csv", rows)
        return rows

    runs_dir = outdir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    v9_script = Path(args.v9_script) if args.v9_script else Path(__file__).with_name("routeB_RT_bem_v9_correction_normalizer.py")
    if not v9_script.exists():
        fallback = Path("/mnt/data/routeB_RT_bem_v9_correction_normalizer.py")
        if fallback.exists():
            v9_script = fallback
        else:
            raise FileNotFoundError(f"BEMv9 script not found: {v9_script}")

    grid = make_grid(args)
    for i, cfg in enumerate(grid, start=1):
        run_id = (
            f"g{i:03d}_nc{cfg['n_center']}_nt{cfg['n_theta']}_ns{cfg['n_sphere']}"
            f"_tf{str(cfg['tube_fraction']).replace('.','p')}_of{str(cfg['outer_factor']).replace('.','p')}"
        )
        run_dir = runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        code, _, _ = run_bemv9(v9_script, args, cfg, run_dir)
        rows.extend(collect_from_bemv9_dir(run_id, run_dir, cfg, returncode=code))

    write_csv(outdir / "normalizer_convergence_grid.csv", rows)
    return rows


def summarize_normalizers(rows: List[Dict[str, Any]], args) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    by_norm: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        norm = str(r.get("normalizer", ""))
        if norm:
            by_norm.setdefault(norm, []).append(r)

    summaries: List[Dict[str, Any]] = []
    for norm, rs in by_norm.items():
        vals = np.asarray([as_float(r.get("alpha_inv_pred_blind_v9")) for r in rs], dtype=float)
        ratios = np.asarray([as_float(r.get("correction_to_leading_ratio")) for r in rs], dtype=float)
        corr = np.asarray([as_float(r.get("DeltaF_phys_normalized")) for r in rs], dtype=float)
        valid = np.isfinite(vals)
        valsv = vals[valid]
        ratiosv = ratios[np.isfinite(ratios)]
        corrv = corr[np.isfinite(corr)]

        n = len(rs)
        pass_count = sum(str(r.get("gate")) == "PASS_SUBLEADING_CORRECTION" for r in rs)
        mean = float(np.mean(valsv)) if len(valsv) else float("nan")
        std = float(np.std(valsv, ddof=1)) if len(valsv) > 1 else (0.0 if len(valsv) == 1 else float("nan"))
        span = float(np.max(valsv) - np.min(valsv)) if len(valsv) else float("nan")
        cv = abs(std / mean) if math.isfinite(mean) and abs(mean) > 1e-300 else float("nan")
        mean_ratio = float(np.mean(np.abs(ratiosv))) if len(ratiosv) else float("nan")
        max_ratio = float(np.max(np.abs(ratiosv))) if len(ratiosv) else float("nan")
        corr_mean = float(np.mean(corrv)) if len(corrv) else float("nan")
        corr_std = float(np.std(corrv, ddof=1)) if len(corrv) > 1 else (0.0 if len(corrv) == 1 else float("nan"))

        enough_grid = n >= args.min_grid_runs
        stable_gate = (
            "PASS_STABLE_NORMALIZER"
            if enough_grid
            and pass_count == n
            and math.isfinite(cv)
            and cv <= args.alpha_cv_threshold
            and math.isfinite(max_ratio)
            and max_ratio <= args.subleading_threshold
            else ("FAIL_NOT_ENOUGH_GRID" if not enough_grid else "FAIL_STABILITY_GATE")
        )

        summaries.append({
            "normalizer": norm,
            "n_runs": n,
            "n_valid": int(np.sum(valid)),
            "pass_count": pass_count,
            "pass_fraction": pass_count / n if n else float("nan"),
            "alpha_inv_blind_mean": mean,
            "alpha_inv_blind_std": std,
            "alpha_inv_blind_span": span,
            "alpha_inv_blind_cv_abs": cv,
            "abs_correction_ratio_mean": mean_ratio,
            "abs_correction_ratio_max": max_ratio,
            "DeltaF_phys_mean": corr_mean,
            "DeltaF_phys_std": corr_std,
            "stability_gate": stable_gate,
        })

    passers = [s for s in summaries if s["stability_gate"] == "PASS_STABLE_NORMALIZER"]
    if passers:
        selected = sorted(passers, key=lambda s: (as_float(s["alpha_inv_blind_cv_abs"], 1e99), as_float(s["abs_correction_ratio_mean"], 1e99)))[0]
    elif summaries:
        selected = sorted(summaries, key=lambda s: (-as_float(s["pass_fraction"], -1), as_float(s["alpha_inv_blind_cv_abs"], 1e99), as_float(s["abs_correction_ratio_mean"], 1e99)))[0]
    else:
        selected = None

    return summaries, selected


def build_selected_budget(rows: List[Dict[str, Any]], selected: Optional[Dict[str, Any]], outdir: Path) -> List[Dict[str, Any]]:
    if not selected:
        write_csv(outdir / "alpha_budget_v10_convergence.csv", [])
        return []
    norm = selected["normalizer"]
    selected_rows = [r for r in rows if r.get("normalizer") == norm]
    out = []
    for r in selected_rows:
        out.append({
            "selected_normalizer": norm,
            "run_id": r.get("run_id"),
            "n_center": r.get("n_center"),
            "n_theta": r.get("n_theta"),
            "n_sphere": r.get("n_sphere"),
            "tube_fraction": r.get("tube_fraction"),
            "outer_factor": r.get("outer_factor"),
            "L_long_target": r.get("L_long_target"),
            "leading_half_alpha_inv": r.get("leading_half_alpha_inv"),
            "DeltaF_pair_raw": r.get("DeltaF_pair_raw"),
            "normalizer_denominator": r.get("normalizer_denominator"),
            "DeltaF_phys_normalized": r.get("DeltaF_phys_normalized"),
            "finite_correction_half": r.get("finite_correction_half"),
            "alpha_inv_pred_blind_v9": r.get("alpha_inv_pred_blind_v9"),
            "correction_to_leading_ratio": r.get("correction_to_leading_ratio"),
            "gate": r.get("gate"),
        })
    write_csv(outdir / "alpha_budget_v10_convergence.csv", out)
    return out


def write_report(outdir: Path, selected: Optional[Dict[str, Any]], selected_rows: List[Dict[str, Any]], args) -> None:
    lines = []
    lines.append("# Blind BEMv10 normalizer-convergence report")
    lines.append("")
    lines.append("This report is alpha-blind: it does not contain or compare with observed alpha.")
    lines.append("")
    lines.append("BEMv10 tests whether a BEMv9 finite-correction normalizer remains stable under mesh/tube/outer-boundary refinement.")
    lines.append("")
    lines.append("## Selected normalizer")
    lines.append("")
    if selected:
        for k, v in selected.items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- no selected normalizer")
    lines.append("")
    lines.append("## Stability rule")
    lines.append("")
    lines.append(f"- minimum grid runs: `{args.min_grid_runs}`")
    lines.append(f"- `alpha_inv_blind_cv_abs <= {args.alpha_cv_threshold}`")
    lines.append(f"- `abs_correction_ratio_max <= {args.subleading_threshold}`")
    lines.append("- all runs must pass `PASS_SUBLEADING_CORRECTION`")
    lines.append("")
    lines.append("No target alpha value is used.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if selected and selected.get("stability_gate") == "PASS_STABLE_NORMALIZER":
        lines.append("The selected normalizer passes this convergence grid. This is still not a derivation; it needs a larger grid and analytic justification.")
    elif selected and selected.get("stability_gate") == "FAIL_NOT_ENOUGH_GRID":
        lines.append("The selected normalizer is only diagnostic because the supplied/reused grid is too small.")
    else:
        lines.append("No normalizer passes the full stability gate on this grid.")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `normalizer_convergence_grid.csv`")
    lines.append("- `normalizer_stability_summary.csv`")
    lines.append("- `alpha_budget_v10_convergence.csv`")
    lines.append("- `runs/<run_id>/` if internal BEMv9 runs were launched")
    (outdir / "blind_alpha_convergence_v10.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v10")
    ap.add_argument("--v9-script", default="")
    ap.add_argument("--v8-script", default="")
    ap.add_argument("--from-bemv9-outdirs", default="", help="comma-separated existing BEMv9 output folders")

    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1")
    ap.add_argument("--target", default="3_1")
    ap.add_argument("--reference", default="0_1")

    ap.add_argument("--grid-json", default="")
    ap.add_argument("--grid-mode", choices=["paired", "cartesian"], default="paired")
    ap.add_argument("--n-center-list", default="8,10,12")
    ap.add_argument("--n-theta-list", default="3,3,4")
    ap.add_argument("--n-sphere-list", default="14,18,24")
    ap.add_argument("--tube-fraction-list", default="0.38,0.32,0.28")
    ap.add_argument("--outer-factor-list", default="2.2,2.6,3.0")

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

    ap.add_argument("--length-samples", type=int, default=4000)
    ap.add_argument("--length-source", choices=["geometric_raw", "spectral_norm", "spectral_norm_rescaled_to_geom_ref"], default="geometric_raw")
    ap.add_argument("--length-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--length-coeff", default="A_M")
    ap.add_argument("--length-fit-min-M", type=int, default=4)
    ap.add_argument("--length-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--pair-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--pair-fit-min-M", type=int, default=4)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--normalizers", default="raw,Mmax,sqrtM,L,L2,L3,NsoftV,NsoftV_L,leading_full,leading_half,M_L,sqrtM_L,M_L2")
    ap.add_argument("--subleading-threshold", type=float, default=0.05)
    ap.add_argument("--alpha-cv-threshold", type=float, default=0.01)
    ap.add_argument("--min-grid-runs", type=int, default=3)

    ap.add_argument("--subrun-timeout", type=int, default=180)
    ap.add_argument("--grid-run-timeout", type=int, default=260)

    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = build_grid_rows(outdir, args)
    summaries, selected = summarize_normalizers(rows, args)
    write_csv(outdir / "normalizer_stability_summary.csv", summaries)
    selected_rows = build_selected_budget(rows, selected, outdir)
    write_report(outdir, selected, selected_rows, args)

    config = {"args": vars(args)}
    (outdir / "run_config_v10.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("Route B BEMv10 normalizer-convergence audit complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    if selected:
        print(f"selected normalizer: {selected.get('normalizer')}")
        print(f"stability gate: {selected.get('stability_gate')}")
        print(f"mean blind alpha inverse: {selected.get('alpha_inv_blind_mean')}")
        print(f"CV: {selected.get('alpha_inv_blind_cv_abs')}")
    else:
        print("selected normalizer: none")
    print("wrote: normalizer_convergence_grid.csv, normalizer_stability_summary.csv, alpha_budget_v10_convergence.csv, blind_alpha_convergence_v10.md")


if __name__ == "__main__":
    main()
