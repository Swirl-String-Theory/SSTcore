#!/usr/bin/env python3
r"""
BEMv7 Route-B audit: spectral-length extraction + finite R--T correction budget.

It separates the large leading scale from the small finite correction:

    L_HK(K) = 2*pi * A_lead(K)/A_lead(reference)
    Delta_RT^ren(K/ref) = F_K - F_ref
    alpha_inv_pred_blind = 1/2 * [N_soft V_soft L_HK(target) + Delta_RT^ren]

No CODATA alpha is used or compared.

Outputs:
  hk_length_coefficients.csv
  spectral_length_estimate.csv
  finite_rt_correction.csv
  alpha_component_budget.csv
  blind_alpha_prediction_v7.md

The script can either call BEMv5 to create raw spectra, or reuse an existing
BEMv5 output folder with --from-bemv5-outdir.

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
from typing import Any, Dict, List, Tuple

import numpy as np


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def read_csv(path: Path) -> List[Dict[str, str]]:
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
        w.writerows(rows)


def fnum(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def load_manifest(outdir: Path) -> List[Dict[str, str]]:
    return read_csv(outdir / "raw_spectrum_manifest.csv")


def load_spectra(outdir: Path) -> Dict[str, np.ndarray]:
    spectra: Dict[str, np.ndarray] = {}
    manifest = load_manifest(outdir)
    for r in manifest:
        k = r.get("knot") or r.get("name")
        fn = r.get("raw_spectrum_file")
        if k and fn and (outdir / fn).exists():
            spectra[k] = np.load(outdir / fn)
    if spectra:
        return spectra
    for p in sorted(outdir.glob("raw_spectrum_*.npy")):
        spectra[p.stem.replace("raw_spectrum_", "")] = np.load(p)
    return spectra


def resolve_name(name_or_id: str, names: List[str], manifest: List[Dict[str, str]]) -> str:
    if name_or_id in names:
        return name_or_id
    for r in manifest:
        if r.get("id") == name_or_id and r.get("knot") in names:
            return str(r["knot"])
    parts = str(name_or_id).split(":")
    if len(parts) >= 2:
        cand = f"{parts[0]}_{parts[1]}"
        if cand in names:
            return cand
    raise ValueError(f"Could not resolve {name_or_id!r}; available={names}")


def partial_action(ev: np.ndarray) -> np.ndarray:
    return -np.cumsum(np.log(np.maximum(ev, 1e-300)))


def hk_design(M: np.ndarray, model: str) -> Tuple[np.ndarray, List[str]]:
    """S_M = A_M M + A_sqrtM sqrt(M) + A_logM log(M) + F + tails."""
    Mf = M.astype(float)
    toks = set(t.strip() for t in model.split("+") if t.strip())
    cols: List[np.ndarray] = []
    names: List[str] = []
    if "M" in toks or "hk" in toks:
        cols.append(Mf); names.append("A_M")
    if "sqrtM" in toks or "hk" in toks:
        cols.append(np.sqrt(Mf)); names.append("A_sqrtM")
    if "logM" in toks or "hk" in toks:
        cols.append(np.log(Mf)); names.append("A_logM")
    cols.append(np.ones_like(Mf)); names.append("F")
    if "inv_sqrt" in toks:
        cols.append(Mf ** -0.5); names.append("b_inv_sqrt")
    if "inv" in toks:
        cols.append(Mf ** -1.0); names.append("b_inv")
    if "threehalf" in toks:
        cols.append(Mf ** -1.5); names.append("b_inv_threehalf")
    if "two" in toks:
        cols.append(Mf ** -2.0); names.append("b_inv_two")
    return np.column_stack(cols), names


def fit_hk(ev: np.ndarray, model: str, min_M: int, tail_frac: float) -> Dict[str, Any]:
    S = partial_action(ev)
    maxM = len(S)
    start = max(int(min_M), int(math.ceil((1.0 - tail_frac) * maxM)))
    start = max(1, min(start, maxM))
    M = np.arange(start, maxM + 1, dtype=int)
    Y = S[M - 1]
    X, names = hk_design(M, model)
    if len(M) < X.shape[1] + 1:
        return {"status": "SKIP_TOO_FEW_POINTS", "fit_model": model, "M_min": int(M.min()), "M_max": int(M.max()), "n_points": len(M), "n_params": X.shape[1]}
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    pred = X @ beta
    resid = Y - pred
    dof = max(1, len(Y) - X.shape[1])
    rms = float(math.sqrt(np.mean(resid * resid)))
    sigma2 = float(np.sum(resid * resid) / dof)
    try:
        cov = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    except Exception:
        se = np.full_like(beta, np.nan, dtype=float)
    row: Dict[str, Any] = {"status": "PASS_FIT", "fit_model": model, "M_min": int(M.min()), "M_max": int(M.max()), "n_points": len(M), "n_params": X.shape[1], "rms": rms}
    for n, v, e in zip(names, beta, se):
        row[n] = float(v)
        row[n + "_se"] = float(e)
    return row


def soft_volume(mode: str, value: float) -> float:
    if mode == "none":
        return 0.0
    if mode == "unit_ball":
        return 4.0 * math.pi / 3.0
    if mode == "sphere_surface":
        return 4.0 * math.pi
    if mode == "numeric":
        return float(value)
    raise ValueError(mode)


def run_bemv5(args, outdir: Path) -> Path:
    bemv5_dir = outdir / "bemv5_base"
    bemv5_dir.mkdir(parents=True, exist_ok=True)
    v5_script = Path(args.v5_script) if args.v5_script else Path(__file__).with_name("routeB_RT_bem_v5_soft_hk_falsifier.py")
    if not v5_script.exists():
        fallback = Path("/mnt/data/routeB_RT_bem_v5_soft_hk_falsifier.py")
        if fallback.exists():
            v5_script = fallback
        else:
            raise FileNotFoundError(v5_script)
    cmd = [
        sys.executable, str(v5_script),
        "--ideal", str(args.ideal),
        "--ideal-xml-knot-ids", args.ideal_xml_knot_ids,
        "--outdir", str(bemv5_dir),
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
    ]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.subrun_timeout)
    (bemv5_dir / "bemv5_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (bemv5_dir / "bemv5_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"BEMv5 failed with return code {proc.returncode}; see {bemv5_dir}")
    return bemv5_dir


def build_outputs(outdir: Path, bemv5_dir: Path, args) -> Dict[str, Any]:
    spectra = load_spectra(bemv5_dir)
    manifest = load_manifest(bemv5_dir)
    if not spectra:
        raise RuntimeError(f"No raw_spectrum_*.npy found in {bemv5_dir}")
    names = list(spectra)
    ref = resolve_name(args.reference, names, manifest)
    target = resolve_name(args.target, names, manifest)
    meta = {r.get("knot", ""): r for r in manifest}

    coeff_rows: List[Dict[str, Any]] = []
    for name, ev in spectra.items():
        row = fit_hk(ev, args.length_fit_model, args.length_fit_min_M, args.length_fit_tail_frac)
        row.update({"knot": name, "id": meta.get(name, {}).get("id", ""), "L_database": meta.get(name, {}).get("L_database", meta.get(name, {}).get("L", "")), "n_eigenvalues": int(len(ev)), "S_all": float(partial_action(ev)[-1])})
        coeff_rows.append(row)
    write_csv(outdir / "hk_length_coefficients.csv", coeff_rows)

    coeff = {r["knot"]: r for r in coeff_rows}
    refA = fnum(coeff[ref].get(args.length_coeff))
    refF = fnum(coeff[ref].get("F"))

    length_rows: List[Dict[str, Any]] = []
    finite_rows: List[Dict[str, Any]] = []
    for name, row in coeff.items():
        A = fnum(row.get(args.length_coeff))
        F = fnum(row.get("F"))
        Lhk = 2.0 * math.pi * A / refA if math.isfinite(refA) and abs(refA) > 1e-300 else float("nan")
        length_rows.append({"knot": name, "reference": ref, "length_coeff": args.length_coeff, "A_lead": A, "A_reference": refA, "L_HK": Lhk, "L_database": row.get("L_database", ""), "ratio_to_reference": A / refA if abs(refA) > 1e-300 else float("nan"), "status": "SPECTRAL_LENGTH_FROM_HK_COEFFICIENT"})
        delta = F - refF
        finite_rows.append({"knot": name, "reference": ref, "F_knot": F, "F_reference": refF, "Delta_RT_ren": delta, "half_Delta_RT_ren": 0.5 * delta, "status": "FINITE_RT_CORRECTION_FROM_CONSTANT_TERM"})
    write_csv(outdir / "spectral_length_estimate.csv", length_rows)
    write_csv(outdir / "finite_rt_correction.csv", finite_rows)

    V = soft_volume(args.soft_volume_mode, args.soft_volume_value)
    Ssoft_per_length = int(args.soft_index_count) * V
    Ltarget = next(r for r in length_rows if r["knot"] == target)["L_HK"]
    Dtarget = next(r for r in finite_rows if r["knot"] == target)["Delta_RT_ren"]
    leading = 0.5 * Ssoft_per_length * Ltarget
    corr = 0.5 * Dtarget
    pred = leading + corr
    budget = {"target": target, "reference": ref, "soft_index_count": int(args.soft_index_count), "soft_volume_mode": args.soft_volume_mode, "soft_volume": V, "S_soft_per_unit_length": Ssoft_per_length, "length_coeff": args.length_coeff, "L_HK_target": Ltarget, "leading_length_term_half_NsoftVsoftL": leading, "Delta_RT_ren_target_reference": Dtarget, "finite_correction_half": corr, "alpha_inv_pred_blind_v7": pred, "status": "ALPHA_BLIND_COMPONENT_BUDGET_NOT_CODATA_COMPARISON"}
    write_csv(outdir / "alpha_component_budget.csv", [budget])
    return {"spectra": spectra, "manifest": manifest, "coeff_rows": coeff_rows, "length_rows": length_rows, "finite_rows": finite_rows, "budget": budget, "target": target, "reference": ref}


def write_report(outdir: Path, result: Dict[str, Any], args, source: str) -> None:
    b = result["budget"]
    lines = [
        "# Blind BEMv7 spectral-length alpha budget", "",
        "This report is alpha-blind: it does not contain or compare against CODATA alpha.", "",
        "BEMv7 uses the working Route-B split", "",
        r"\[",
        r"\alpha^{-1}_{\rm pred,blind}=\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm HK}(3_1)+\Delta_{\rm RT}^{\rm ren}(3_1/0_1)\right].",
        r"\]", "",
        "This is a falsifiable component budget, not yet a theorem.", "",
        "## Spectral length", "",
        r"\[L_{\rm HK}(K)=2\pi\,A_{\rm lead}(K)/A_{\rm lead}(0_1).\]", "",
        f"- length coefficient: `{args.length_coeff}`",
        f"- length fit model: `{args.length_fit_model}`", "",
        "## Component budget", "",
    ]
    for k, v in b.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Outputs", "", "- `hk_length_coefficients.csv`", "- `spectral_length_estimate.csv`", "- `finite_rt_correction.csv`", "- `alpha_component_budget.csv`", "- `bemv5_base/` or reused BEMv5 folder with raw spectra", "", "## Interpretation", "", "The next gate is convergence: `L_HK`, `Delta_RT^ren`, and the total blind budget must stabilize under mesh, tube-radius, and outer-boundary refinement.", "", f"Input/source: `{source}`"]
    (outdir / "blind_alpha_prediction_v7.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v7")
    ap.add_argument("--v5-script", default="")
    ap.add_argument("--from-bemv5-outdir", default="")
    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1")
    ap.add_argument("--target", default="3_1")
    ap.add_argument("--reference", default="0_1")
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
    ap.add_argument("--length-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--length-coeff", default="A_M", help="A_M, A_sqrtM, or A_logM")
    ap.add_argument("--length-fit-min-M", type=int, default=4)
    ap.add_argument("--length-fit-tail-frac", type=float, default=0.75)
    ap.add_argument("--subrun-timeout", type=int, default=300)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if args.from_bemv5_outdir:
        bemv5_dir = Path(args.from_bemv5_outdir)
        source = f"existing BEMv5 outdir={bemv5_dir}"
    else:
        bemv5_dir = run_bemv5(args, outdir)
        source = f"BEMv5 subrun={bemv5_dir}"
    result = build_outputs(outdir, bemv5_dir, args)
    write_report(outdir, result, args, source)
    (outdir / "run_config_v7.json").write_text(json.dumps({"args": vars(args), "source": source, "bemv5_dir": str(bemv5_dir)}, indent=2, sort_keys=True), encoding="utf-8")

    b = result["budget"]
    print("=" * 78)
    print("Route B BEMv7 spectral-length budget complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"source: {source}")
    print(f"target/reference: {result['target']}/{result['reference']}")
    print(f"L_HK_target = {b['L_HK_target']}")
    print(f"leading length term = {b['leading_length_term_half_NsoftVsoftL']}")
    print(f"finite correction half = {b['finite_correction_half']}")
    print(f"alpha_inv_pred_blind_v7 = {b['alpha_inv_pred_blind_v7']}")
    print("wrote: hk_length_coefficients.csv, spectral_length_estimate.csv, finite_rt_correction.csv, alpha_component_budget.csv, blind_alpha_prediction_v7.md")


if __name__ == "__main__":
    main()
