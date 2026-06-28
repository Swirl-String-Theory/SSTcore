#!/usr/bin/env python3
r"""
routeB_RT_bem_v6_convergence_grid.py
====================================

BEMv6 Route-B audit: convergence-grid wrapper around BEMv5.

BEMv5 separated

    S_total = S_soft + S_RT^ren

and produced raw spectra, cutoff series, heat-kernel counterterms, and a blind
alpha prediction for one mesh/operator run.

BEMv6 runs BEMv5 across a mesh/tube/outer-boundary grid and fits the continuum
trend

    A(h,a,R) = A_inf + c_h h^p + c_a a^q + c_R R^{-r} + ...

where

    A(h,a,R) = alpha_inv_pred_blind_with_soft
             = 1/2 (S_soft + S_RT^ren)

from BEMv5's heat-kernel counterterm file.

New BEMv6 outputs
-----------------
  convergence_grid.csv
      One row per BEMv5 sub-run with mesh/tube/outer parameters and blind value.

  continuum_limit_fit.csv
      Fits over the grid for alpha_inv_pred_blind_with_soft and S_total.

  blind_alpha_convergence.md
      Alpha-blind convergence report. No CODATA alpha comparison.

  runs/<run_id>/
      Full BEMv5 output directory for each grid point.

This is still a falsifier/provenance harness. It does not prove or fit alpha.

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
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np


def parse_list_int(s: str) -> List[int]:
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_float(s: str) -> List[float]:
    return [float(x.strip()) for x in str(s).split(",") if x.strip()]


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


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
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def as_float(row: Dict[str, Any], key: str, default=float("nan")) -> float:
    try:
        return float(row.get(key, default))
    except Exception:
        return default


def select_best_hk_fit(rows: List[Dict[str, str]], target_name: str, prefer_model: str = "") -> Optional[Dict[str, str]]:
    valid = [
        r for r in rows
        if r.get("status") == "PASS_FIT"
        and str(r.get("target_selected", "")).lower() in {"true", "1", "yes"}
    ]
    if target_name:
        valid2 = [r for r in valid if r.get("knot") == target_name or r.get("target") == target_name]
        if valid2:
            valid = valid2
    if prefer_model:
        preferred = [r for r in valid if r.get("counterterm_model") == prefer_model]
        if preferred:
            valid = preferred
    if not valid:
        return None
    return sorted(valid, key=lambda r: as_float(r, "rms", 1e99))[0]


def run_bemv5_for_config(v5_script: Path, args, cfg: Dict[str, Any], run_dir: Path) -> Tuple[int, str, str]:
    cmd = [
        sys.executable, str(v5_script),
        "--ideal", str(args.ideal),
        "--ideal-xml-knot-ids", args.ideal_xml_knot_ids,
        "--outdir", str(run_dir),
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
    ]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.subrun_timeout)
    (run_dir / "bemv5_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (run_dir / "bemv5_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def make_grid(args) -> List[Dict[str, Any]]:
    if args.grid_json:
        return json.loads(Path(args.grid_json).read_text(encoding="utf-8"))

    n_centers = parse_list_int(args.n_center_list)
    n_thetas = parse_list_int(args.n_theta_list)
    n_spheres = parse_list_int(args.n_sphere_list)
    tube_fracs = parse_list_float(args.tube_fraction_list)
    outer_factors = parse_list_float(args.outer_factor_list)

    if args.grid_mode == "paired":
        # Pair indices across lists; last value repeats if a list is shorter.
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

    # Cartesian grid.
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


def continuum_design_matrix(rows: List[Dict[str, Any]], model: str) -> Tuple[np.ndarray, List[str]]:
    h = np.asarray([float(r["h"]) for r in rows], dtype=float)
    a = np.asarray([float(r["tube_fraction"]) for r in rows], dtype=float)
    Rinv = 1.0 / np.asarray([float(r["outer_factor"]) for r in rows], dtype=float)
    n = np.asarray([float(r["selected_nodes"]) for r in rows], dtype=float)
    cols = [np.ones(len(rows))]
    names = ["A_inf"]

    tokens = set(t.strip() for t in model.split("+") if t.strip())
    if "h" in tokens:
        cols.append(h); names.append("c_h")
    if "h2" in tokens:
        cols.append(h*h); names.append("c_h2")
    if "a" in tokens:
        cols.append(a); names.append("c_a")
    if "a2" in tokens:
        cols.append(a*a); names.append("c_a2")
    if "Rinv" in tokens:
        cols.append(Rinv); names.append("c_Rinv")
    if "Rinv2" in tokens:
        cols.append(Rinv*Rinv); names.append("c_Rinv2")
    if "Ninv" in tokens:
        cols.append(1.0 / np.maximum(n, 1.0)); names.append("c_Ninv")
    return np.column_stack(cols), names


def fit_continuum(rows: List[Dict[str, Any]], y_key: str, model: str) -> Dict[str, Any]:
    good = [r for r in rows if math.isfinite(as_float(r, y_key))]
    if len(good) < 2:
        return {"quantity": y_key, "model": model, "status": "SKIP_TOO_FEW_ROWS"}

    y = np.asarray([as_float(r, y_key) for r in good], dtype=float)
    X, names = continuum_design_matrix(good, model)
    if len(good) < X.shape[1] + 1:
        return {
            "quantity": y_key,
            "model": model,
            "status": "SKIP_UNDERDETERMINED",
            "n_rows": len(good),
            "n_params": X.shape[1],
        }

    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    resid = y - pred
    dof = max(1, len(y) - X.shape[1])
    rms = float(math.sqrt(np.mean(resid * resid)))
    sigma2 = float(np.sum(resid * resid) / dof)
    try:
        cov = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    except Exception:
        se = np.full_like(beta, np.nan, dtype=float)

    out: Dict[str, Any] = {
        "quantity": y_key,
        "model": model,
        "status": "PASS_FIT",
        "n_rows": len(good),
        "n_params": X.shape[1],
        "rms": rms,
        "A_inf": float(beta[0]),
        "A_inf_se": float(se[0]) if len(se) else float("nan"),
    }
    for name, val, err in zip(names[1:], beta[1:], se[1:]):
        out[name] = float(val)
        out[name + "_se"] = float(err)
    return out


def write_report(outdir: Path, grid_rows: List[Dict[str, Any]], fit_rows: List[Dict[str, Any]], args) -> None:
    selected = [
        r for r in fit_rows
        if r.get("quantity") == "alpha_inv_pred_blind_with_soft"
        and r.get("status") == "PASS_FIT"
    ]
    if selected:
        best = sorted(selected, key=lambda r: as_float(r, "rms", 1e99))[0]
    else:
        best = {"status": "NO_VALID_CONTINUUM_FIT"}

    lines: List[str] = []
    lines.append("# Blind BEMv6 convergence-grid report")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("This report is alpha-blind. It does not contain or compare with observed alpha.")
    lines.append("")
    lines.append("BEMv6 fits convergence over mesh/tube/outer-boundary parameters:")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"A(h,a,R)=A_\infty+c_hh+c_aa+c_RR^{-1}+\cdots .")
    lines.append(r"\]")
    lines.append("")
    lines.append("where \(A\) is the BEMv5 blind quantity")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"A=\frac12\left(S_{\rm soft}+S_{\rm RT}^{\rm ren}\right).")
    lines.append(r"\]")
    lines.append("")
    lines.append("## Grid")
    lines.append("")
    lines.append(f"- subruns: `{len(grid_rows)}`")
    lines.append(f"- target: `{args.target}`")
    lines.append(f"- reference: `{args.reference}`")
    lines.append(f"- grid mode: `{args.grid_mode}`")
    lines.append("")
    lines.append("## Selected continuum fit")
    lines.append("")
    for k, v in best.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("A stable BEMv6 result requires the continuum estimate to remain stable under expanded grids and alternative counterterm models.")
    lines.append("If the estimate changes sign, scale, or model selection under refinement, the present Route-B operator is not yet a fine-structure derivation.")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `convergence_grid.csv`: all subrun values")
    lines.append("- `continuum_limit_fit.csv`: continuum extrapolation fits")
    lines.append("- `runs/<run_id>/`: full BEMv5 outputs for each grid point")
    (outdir / "blind_alpha_convergence.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v6")
    ap.add_argument("--v5-script", default=None, help="path to routeB_RT_bem_v5_soft_hk_falsifier.py")
    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1")
    ap.add_argument("--target", default="3_1")
    ap.add_argument("--reference", default="0_1")

    ap.add_argument("--grid-json", default="")
    ap.add_argument("--grid-mode", choices=["paired", "cartesian"], default="paired")
    ap.add_argument("--n-center-list", default="10,12,14")
    ap.add_argument("--n-theta-list", default="3,4,4")
    ap.add_argument("--n-sphere-list", default="18,24,32")
    ap.add_argument("--tube-fraction-list", default="0.35,0.30,0.25")
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
    ap.add_argument("--prefer-counterterm-model", default="", help="optional exact model name to select from BEMv5 rows")

    ap.add_argument("--soft-index-count", type=int, default=4)
    ap.add_argument("--soft-volume-mode", choices=["none", "unit_ball", "sphere_surface", "numeric"], default="unit_ball")
    ap.add_argument("--soft-volume-value", type=float, default=0.0)

    ap.add_argument("--continuum-models", default="h+a+Rinv,h+a+Rinv+Ninv,h+h2+a+Rinv")
    ap.add_argument("--subrun-timeout", type=int, default=300)

    args = ap.parse_args()

    outdir = Path(args.outdir)
    runs_dir = outdir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    v5_script = Path(args.v5_script) if args.v5_script else Path(__file__).with_name("routeB_RT_bem_v5_soft_hk_falsifier.py")
    if not v5_script.exists():
        fallback = Path("/mnt/data/routeB_RT_bem_v5_soft_hk_falsifier.py")
        if fallback.exists():
            v5_script = fallback
        else:
            raise FileNotFoundError(f"BEMv5 script not found: {v5_script}")

    grid = make_grid(args)
    grid_rows: List[Dict[str, Any]] = []

    for i, cfg in enumerate(grid, start=1):
        run_id = (
            f"g{i:03d}_nc{cfg['n_center']}_nt{cfg['n_theta']}_ns{cfg['n_sphere']}"
            f"_tf{str(cfg['tube_fraction']).replace('.','p')}_of{str(cfg['outer_factor']).replace('.','p')}"
        )
        run_dir = runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        code, stdout, stderr = run_bemv5_for_config(v5_script, args, cfg, run_dir)
        hk_rows = read_csv_rows(run_dir / "heat_kernel_counterterms.csv")
        manifest_rows = read_csv_rows(run_dir / "raw_spectrum_manifest.csv")
        best = select_best_hk_fit(hk_rows, args.target, args.prefer_counterterm_model)

        selected_nodes = float("nan")
        raw_modes_target = float("nan")
        if manifest_rows:
            for mr in manifest_rows:
                if mr.get("knot") == args.target or mr.get("id") == args.target:
                    selected_nodes = as_float(mr, "selected_nodes")
                    raw_modes_target = as_float(mr, "n_eigenvalues")
                    break
            if not math.isfinite(selected_nodes):
                selected_nodes = as_float(manifest_rows[0], "selected_nodes")

        row: Dict[str, Any] = {
            "run_id": run_id,
            "returncode": code,
            "n_center": cfg["n_center"],
            "n_theta": cfg["n_theta"],
            "n_sphere": cfg["n_sphere"],
            "tube_fraction": cfg["tube_fraction"],
            "outer_factor": cfg["outer_factor"],
            "h": 1.0 / float(cfg["n_center"]),
            "Rinv": 1.0 / float(cfg["outer_factor"]),
            "selected_nodes": selected_nodes,
            "raw_modes_target": raw_modes_target,
            "run_dir": str(run_dir),
        }
        if best:
            for k in [
                "counterterm_model", "status", "rms", "S_ren", "S_ren_se",
                "soft_action", "S_total_soft_plus_RT", "alpha_inv_pred_blind_with_soft",
                "alpha_inv_half_RT_only", "M_min", "M_max", "n_points",
            ]:
                row[k] = best.get(k, "")
        else:
            row["status"] = "NO_VALID_BEMV5_FIT"
        grid_rows.append(row)

    write_csv(outdir / "convergence_grid.csv", grid_rows)

    fit_rows: List[Dict[str, Any]] = []
    for model in [m.strip() for m in args.continuum_models.split(",") if m.strip()]:
        for q in ["alpha_inv_pred_blind_with_soft", "S_total_soft_plus_RT", "S_ren"]:
            fit_rows.append(fit_continuum(grid_rows, q, model))
    write_csv(outdir / "continuum_limit_fit.csv", fit_rows)
    write_report(outdir, grid_rows, fit_rows, args)

    config = {"args": vars(args), "grid": grid, "v5_script": str(v5_script)}
    (outdir / "run_config_v6.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("Route B BEMv6 convergence-grid audit complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"subruns: {len(grid_rows)}")
    for r in grid_rows:
        print(
            f"{r['run_id']:45s} rc={r['returncode']} "
            f"A={r.get('alpha_inv_pred_blind_with_soft','')} "
            f"S_total={r.get('S_total_soft_plus_RT','')} "
            f"model={r.get('counterterm_model','')}"
        )
    print("wrote: convergence_grid.csv, continuum_limit_fit.csv, blind_alpha_convergence.md, runs/<run_id>/...")


if __name__ == "__main__":
    main()
