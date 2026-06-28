#!/usr/bin/env python3
r"""
routeB_RT_bem_v8_pair_length_budget.py
======================================

BEMv8 Route-B audit: absolute longitudinal scale + direct pair-subtracted
finite R--T correction.

Motivation
----------
BEMv7 showed two failures:

  1. The old spectral length extractor used spectra from unit-arclength
     normalized geometry. It therefore could not recover the absolute
     ideal-knot longitudinal measure.

  2. The finite correction was taken as F_K - F_ref from two independent fits,
     which is badly conditioned.

BEMv8 fixes both:

  A. The large length term is taken from the alpha-blind raw Fourier arclength
     of the ideal-knot data, not from the database L column and not from CODATA.
     A spectral coefficient diagnostic is still written.

  B. The finite correction is fitted directly from the pair-subtracted series

        DeltaS_M(K/ref) = S_M(K) - S_M(ref)

     using one fit:

        DeltaS_M = d_M M + d_sqrt sqrt(M) + d_log log(M)
                   + DeltaF_pair
                   + d_-1/2 M^-1/2 + d_-1 M^-1 + ...

The blind budget is

  alpha_inv_pred_blind_v8 =
      1/2 [ N_soft V_soft L_long(3_1)
            + DeltaF_pair(3_1/0_1) ].

No observed alpha is used or compared.

Outputs
-------
  geometric_length_audit.csv
  hk_length_coefficients_phys.csv
  spectral_length_estimate_phys.csv
  pair_subtracted_correction.csv
  alpha_component_budget_v8.csv
  blind_alpha_prediction_v8.md

BEMv8 can run BEMv5 to generate spectra, or reuse an existing BEMv5 output
folder via --from-bemv5-outdir.

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
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Utility I/O
# ---------------------------------------------------------------------------

def safe_name(s: str) -> str:
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
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def parse_id_csv(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def load_manifest(outdir: Path) -> List[Dict[str, str]]:
    return read_csv_rows(outdir / "raw_spectrum_manifest.csv")


def load_spectra(outdir: Path) -> Dict[str, np.ndarray]:
    spectra: Dict[str, np.ndarray] = {}
    manifest = load_manifest(outdir)
    if manifest:
        for row in manifest:
            knot = row.get("knot") or row.get("name")
            fn = row.get("raw_spectrum_file")
            if knot and fn and (outdir / fn).exists():
                spectra[knot] = np.load(outdir / fn)
    if not spectra:
        for p in outdir.glob("raw_spectrum_*.npy"):
            name = p.stem.replace("raw_spectrum_", "")
            spectra[name] = np.load(p)
    return spectra


def resolve_name(name_or_id: str, names: List[str], manifest: List[Dict[str, str]]) -> str:
    if name_or_id in names:
        return name_or_id
    for row in manifest:
        if row.get("id") == name_or_id and row.get("knot") in names:
            return str(row["knot"])
    parts = str(name_or_id).split(":")
    if len(parts) >= 2:
        cand = f"{parts[0]}_{parts[1]}"
        if cand in names:
            return cand
    raise ValueError(f"Could not resolve {name_or_id!r}; available={names}")


# ---------------------------------------------------------------------------
# Ideal XML/Fourier parser for physical longitudinal length
# ---------------------------------------------------------------------------

def parse_attrs_from_tag(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def parse_vec3_attr(s: str) -> np.ndarray:
    vals = [float(x.strip()) for x in s.split(",")]
    if len(vals) != 3:
        raise ValueError(f"expected 3-vector, got {s!r}")
    return np.asarray(vals, dtype=float)


def ideal_id_to_name(bid: str) -> str:
    parts = str(bid).split(":")
    if len(parts) >= 3:
        return f"{parts[0]}_{parts[2]}"
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return str(bid).replace(":", "_")


def is_xml_ideal(path: Path) -> bool:
    if not path.exists():
        return False
    head = path.read_text(encoding="utf-8", errors="replace")[:8192]
    return "<AB " in head and "<Coeff " in head


def parse_xml_ideal_blocks(path: Path) -> Dict[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"<AB\b([^>]*)>(.*?)</AB>", text, flags=re.S | re.I):
        attrs = parse_attrs_from_tag(m.group(1))
        bid = attrs.get("Id", f"AB_{len(blocks)+1}")
        body = m.group(2)
        ncomp = int(attrs.get("n", "1").strip() or "1")
        supported = (ncomp == 1 and "<Component" not in body)
        A: Dict[int, np.ndarray] = {}
        B: Dict[int, np.ndarray] = {}
        if supported:
            for cm in re.finditer(r"<Coeff\b([^>]*)/?>", body, flags=re.I):
                ca = parse_attrs_from_tag(cm.group(1))
                if not all(k in ca for k in ("I", "A", "B")):
                    continue
                idx = int(ca["I"])
                A[idx] = parse_vec3_attr(ca["A"])
                B[idx] = parse_vec3_attr(ca["B"])
            supported = bool(A and B)

        def ffloat(k: str):
            try:
                return float(str(attrs.get(k, "")).strip())
            except Exception:
                return None

        blocks[bid] = {
            "id": bid,
            "name": ideal_id_to_name(bid),
            "conway": attrs.get("Conway", ""),
            "L_database": ffloat("L"),
            "D_database": ffloat("D"),
            "n": ncomp,
            "supported": supported,
            "A": A,
            "B": B,
            "source": "xml_fourier",
        }
    return blocks


def generated_unknot_block() -> Dict[str, Any]:
    return {
        "id": "0:1:1",
        "name": "0_1",
        "conway": "0",
        "L_database": 2.0 * math.pi,
        "D_database": 1.0,
        "n": 1,
        "supported": True,
        "A": {1: np.asarray([1.0, 0.0, 0.0], dtype=float)},
        "B": {1: np.asarray([0.0, 1.0, 0.0], dtype=float)},
        "source": "generated_unit_circle_control",
    }


def eval_fourier_block(block: Dict[str, Any], samples: int) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * math.pi, int(samples), endpoint=False)
    pts = np.zeros((len(t), 3), dtype=float)
    A: Dict[int, np.ndarray] = block["A"]
    B: Dict[int, np.ndarray] = block["B"]
    for I in sorted(set(A) | set(B)):
        pts += np.cos(I * t)[:, None] * A.get(I, np.zeros(3))[None, :]
        pts += np.sin(I * t)[:, None] * B.get(I, np.zeros(3))[None, :]
    return pts


def arclength_closed(P: np.ndarray) -> float:
    Q = np.vstack([P, P[0]])
    return float(np.sum(np.linalg.norm(np.diff(Q, axis=0), axis=1)))


def parse_coordinate_blocks(path: Path) -> Dict[str, Dict[str, Any]]:
    blocks: Dict[str, Dict[str, Any]] = {}
    cur_name: Optional[str] = None
    cur_pts: List[List[float]] = []
    anon = 1

    def flush():
        nonlocal cur_name, cur_pts, anon
        if cur_pts:
            nm = cur_name or f"knot_{anon}"
            anon += 1
            base, k = nm, 2
            while nm in blocks:
                nm = f"{base}__{k}"
                k += 1
            blocks[nm] = {
                "id": nm,
                "name": nm,
                "conway": "",
                "L_database": None,
                "D_database": None,
                "n": 1,
                "supported": True,
                "points": np.asarray(cur_pts, dtype=float),
                "source": "coordinate_block",
            }
        cur_name, cur_pts = None, []

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith(("#", "//", ";")):
            s = line.lstrip("#/;").strip()
            m = re.search(r"(?:knot|name|id)\s*[:=]\s*([A-Za-z0-9_+\-.]+)", s, re.I)
            if m:
                flush()
                cur_name = m.group(1)
            continue
        parts = [p for p in re.split(r"[,;\s]+", line) if p]
        vals = []
        for p in parts:
            try:
                vals.append(float(p))
            except Exception:
                pass
        if len(vals) >= 3:
            cur_pts.append(vals[-3:])
        elif re.match(r"^[A-Za-z0-9_+\-.]+$", line):
            flush()
            cur_name = line
    flush()
    return blocks


def load_physical_blocks(path: Path, requested_ids: str, auto_add_unknot: bool, samples: int) -> Dict[str, Dict[str, Any]]:
    if is_xml_ideal(path):
        blocks_by_id = parse_xml_ideal_blocks(path)
        blocks_by_name = {b["name"]: b for b in blocks_by_id.values() if b.get("supported")}
        selected: Dict[str, Dict[str, Any]] = {}
        ids = parse_id_csv(requested_ids)

        if len(ids) == 1 and ids[0].lower() == "all":
            if auto_add_unknot and "0:1:1" not in blocks_by_id:
                b = generated_unknot_block()
                selected[b["name"]] = b
            for b in blocks_by_id.values():
                if b.get("supported"):
                    selected[b["name"]] = b
            return selected

        for token in ids:
            b = blocks_by_id.get(token)
            if b is None:
                # Also allow display names.
                b = blocks_by_name.get(token)
            if b is None and auto_add_unknot and token in {"0:1:1", "0_1"}:
                b = generated_unknot_block()
            if b is None:
                raise ValueError(f"requested knot {token!r} not found in {path}")
            if not b.get("supported"):
                raise ValueError(f"requested knot {token!r} is multi-component or unsupported")
            selected[b["name"]] = b
        return selected

    blocks = parse_coordinate_blocks(path)
    if auto_add_unknot and "0_1" not in blocks and ("0:1:1" in requested_ids or "0_1" in requested_ids):
        blocks["0_1"] = generated_unknot_block()
    return blocks


def make_geometric_length_audit(path: Path, requested_ids: str, args) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    blocks = load_physical_blocks(path, requested_ids, auto_add_unknot=(not args.no_auto_add_unknot), samples=args.length_samples)
    rows: List[Dict[str, Any]] = []
    lengths: Dict[str, float] = {}
    for name, block in blocks.items():
        if "points" in block:
            P = np.asarray(block["points"], dtype=float)
        else:
            P = eval_fourier_block(block, args.length_samples)
        L_raw = arclength_closed(P)
        # For the analytic generated circle, use the exact value as the reference length.
        if block.get("source") == "generated_unit_circle_control":
            L_raw = 2.0 * math.pi
        L_db = block.get("L_database")
        rel = (L_raw - float(L_db)) / float(L_db) if L_db not in (None, "") and abs(float(L_db)) > 0 else float("nan")
        rows.append({
            "knot": name,
            "id": block.get("id", name),
            "source": block.get("source", ""),
            "length_samples": int(args.length_samples),
            "L_raw_arclength": float(L_raw),
            "L_database": L_db if L_db is not None else "",
            "relative_error_vs_database": rel,
            "status": "ALPHA_BLIND_RAW_FOURIER_ARCLENGTH",
        })
        lengths[name] = float(L_raw)
    return rows, lengths


# ---------------------------------------------------------------------------
# BEMv5 execution and spectra
# ---------------------------------------------------------------------------

def run_bemv5(v5_script: Path, args, outdir: Path) -> None:
    cmd = [
        sys.executable, str(v5_script),
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
    ]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.subrun_timeout)
    (outdir / "bemv5_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (outdir / "bemv5_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"BEMv5 subrun failed with return code {proc.returncode}; see {outdir}/bemv5_stderr.txt")


# ---------------------------------------------------------------------------
# Fits: individual spectral diagnostics and direct pair correction
# ---------------------------------------------------------------------------

def partial_action(ev: np.ndarray) -> np.ndarray:
    return -np.cumsum(np.log(np.maximum(ev, 1e-300)))


def hk_design(M: np.ndarray, model: str, include_constant: bool = True) -> Tuple[np.ndarray, List[str]]:
    Mf = M.astype(float)
    tokens = set(t.strip() for t in str(model).split("+") if t.strip())
    cols: List[np.ndarray] = []
    names: List[str] = []
    if "M" in tokens or "hk" in tokens:
        cols.append(Mf); names.append("A_M")
    if "sqrtM" in tokens or "hk" in tokens:
        cols.append(np.sqrt(Mf)); names.append("A_sqrtM")
    if "logM" in tokens or "hk" in tokens:
        cols.append(np.log(Mf)); names.append("A_logM")
    if include_constant:
        cols.append(np.ones_like(Mf)); names.append("F")
    if "inv_sqrt" in tokens:
        cols.append(Mf ** -0.5); names.append("b_inv_sqrt")
    if "inv" in tokens:
        cols.append(Mf ** -1.0); names.append("b_inv")
    if "threehalf" in tokens:
        cols.append(Mf ** -1.5); names.append("b_inv_threehalf")
    if "two" in tokens:
        cols.append(Mf ** -2.0); names.append("b_inv_two")
    return np.column_stack(cols), names


def fit_series(Y_full: np.ndarray, model: str, min_M: int, tail_frac: float) -> Dict[str, Any]:
    maxM = len(Y_full)
    start = max(int(min_M), int(math.ceil((1.0 - tail_frac) * maxM)))
    start = max(1, min(start, maxM))
    M = np.arange(start, maxM + 1, dtype=int)
    Y = Y_full[M - 1]

    X, names = hk_design(M, model, include_constant=True)
    if len(M) < X.shape[1] + 1:
        return {"status": "SKIP_TOO_FEW_POINTS", "fit_model": model, "M_min": int(M[0]), "M_max": int(M[-1]), "n_points": int(len(M)), "n_params": int(X.shape[1])}

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

    row: Dict[str, Any] = {
        "status": "PASS_FIT",
        "fit_model": model,
        "M_min": int(M[0]),
        "M_max": int(M[-1]),
        "n_points": int(len(M)),
        "n_params": int(X.shape[1]),
        "rms": rms,
    }
    for name, val, err in zip(names, beta, se):
        row[name] = float(val)
        row[name + "_se"] = float(err)
    return row


def soft_volume(args) -> float:
    if args.soft_volume_mode == "none":
        return 0.0
    if args.soft_volume_mode == "unit_ball":
        return 4.0 * math.pi / 3.0
    if args.soft_volume_mode == "sphere_surface":
        return 4.0 * math.pi
    if args.soft_volume_mode == "numeric":
        return float(args.soft_volume_value)
    raise ValueError(args.soft_volume_mode)


def build_outputs(outdir: Path, spectra: Dict[str, np.ndarray], manifest: List[Dict[str, str]], args) -> Dict[str, Any]:
    names = list(spectra.keys())
    reference = resolve_name(args.reference, names, manifest)
    target = resolve_name(args.target, names, manifest)

    geom_rows, geom_lengths = make_geometric_length_audit(Path(args.ideal), args.ideal_xml_knot_ids, args)
    write_csv(outdir / "geometric_length_audit.csv", geom_rows)

    # Individual spectral coefficient diagnostics from the normalized BEM spectra.
    coeff_rows: List[Dict[str, Any]] = []
    for name, ev in spectra.items():
        fit = fit_series(partial_action(ev), args.length_fit_model, args.length_fit_min_M, args.length_fit_tail_frac)
        fit.update({
            "knot": name,
            "n_eigenvalues": int(len(ev)),
            "S_all": float(partial_action(ev)[-1]),
            "status_note": "DIAGNOSTIC_ONLY_NORMALIZED_BEM_SPECTRUM",
        })
        coeff_rows.append(fit)
    write_csv(outdir / "hk_length_coefficients_phys.csv", coeff_rows)

    coeff_by_name = {r["knot"]: r for r in coeff_rows}
    ref_A = as_float(coeff_by_name[reference].get(args.length_coeff))
    length_rows: List[Dict[str, Any]] = []
    for name in names:
        A = as_float(coeff_by_name[name].get(args.length_coeff))
        L_spectral_norm = 2.0 * math.pi * A / ref_A if math.isfinite(A) and math.isfinite(ref_A) and abs(ref_A) > 1e-300 else float("nan")
        L_geom = geom_lengths.get(name, float("nan"))
        if args.length_source == "geometric_raw":
            L_used = L_geom
        elif args.length_source == "spectral_norm":
            L_used = L_spectral_norm
        elif args.length_source == "spectral_norm_rescaled_to_geom_ref":
            L_ref_geom = geom_lengths.get(reference, 2.0 * math.pi)
            L_used = L_ref_geom * A / ref_A if math.isfinite(A) and math.isfinite(ref_A) and abs(ref_A) > 1e-300 else float("nan")
        else:
            raise ValueError(args.length_source)
        length_rows.append({
            "knot": name,
            "reference": reference,
            "length_source": args.length_source,
            "length_coeff": args.length_coeff,
            "A_lead_normalized_spectrum": A,
            "A_reference_normalized_spectrum": ref_A,
            "L_spectral_norm": L_spectral_norm,
            "L_geom_raw": L_geom,
            "L_used": L_used,
            "status": "PHYSICAL_LENGTH_BRANCH_RESTORES_LONGITUDINAL_SCALE",
        })
    write_csv(outdir / "spectral_length_estimate_phys.csv", length_rows)

    # Direct pair-subtracted finite correction.
    Sref = partial_action(spectra[reference])
    pair_rows: List[Dict[str, Any]] = []
    for name, ev in spectra.items():
        if name == reference:
            continue
        S = partial_action(ev)
        maxM = min(len(S), len(Sref))
        delta_series = S[:maxM] - Sref[:maxM]
        fit = fit_series(delta_series, args.pair_fit_model, args.pair_fit_min_M, args.pair_fit_tail_frac)
        deltaF = as_float(fit.get("F"))
        fit.update({
            "knot": name,
            "reference": reference,
            "DeltaF_pair": deltaF,
            "half_DeltaF_pair": 0.5 * deltaF,
            "max_common_modes": int(maxM),
            "status_note": "DIRECT_PAIR_SUBTRACTED_FIT_NO_SEPARATE_FK_MINUS_FREF",
        })
        pair_rows.append(fit)
    write_csv(outdir / "pair_subtracted_correction.csv", pair_rows)

    # Component budget.
    S_soft_per_length = int(args.soft_index_count) * soft_volume(args)
    target_L = next(r for r in length_rows if r["knot"] == target)["L_used"]
    target_pair = next(r for r in pair_rows if r["knot"] == target)
    DeltaF_pair = as_float(target_pair.get("DeltaF_pair"))
    leading = 0.5 * S_soft_per_length * target_L
    correction = 0.5 * DeltaF_pair
    alpha_pred = leading + correction

    budget = {
        "target": target,
        "reference": reference,
        "soft_index_count": int(args.soft_index_count),
        "soft_volume_mode": args.soft_volume_mode,
        "soft_volume": soft_volume(args),
        "S_soft_per_unit_length": S_soft_per_length,
        "length_source": args.length_source,
        "length_coeff": args.length_coeff,
        "L_long_target": target_L,
        "leading_length_term_half_NsoftVsoftL": leading,
        "DeltaF_pair_target_reference": DeltaF_pair,
        "finite_correction_half_pair": correction,
        "alpha_inv_pred_blind_v8": alpha_pred,
        "status": "ALPHA_BLIND_BEMV8_PAIR_LENGTH_BUDGET_NOT_CODATA_COMPARISON",
    }
    write_csv(outdir / "alpha_component_budget_v8.csv", [budget])

    return {
        "target": target,
        "reference": reference,
        "geom_rows": geom_rows,
        "length_rows": length_rows,
        "pair_rows": pair_rows,
        "budget": budget,
    }


def write_report(outdir: Path, result: Dict[str, Any], args, input_source: str) -> None:
    b = result["budget"]
    lines: List[str] = []
    lines.append("# Blind BEMv8 pair-subtracted length budget")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("This report is alpha-blind. It does not contain or compare against observed alpha.")
    lines.append("")
    lines.append("BEMv8 uses")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"\alpha^{-1}_{\rm pred,blind}")
    lines.append(r"=\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm long}(3_1)")
    lines.append(r"+\Delta F_{\rm pair}(3_1/0_1)\right].")
    lines.append(r"\]")
    lines.append("")
    lines.append("The large term uses restored longitudinal scale; the finite term uses direct pair subtraction.")
    lines.append("")
    lines.append("## Component budget")
    lines.append("")
    for k, v in b.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append("- `geometric_length_audit.csv`")
    lines.append("- `hk_length_coefficients_phys.csv`")
    lines.append("- `spectral_length_estimate_phys.csv`")
    lines.append("- `pair_subtracted_correction.csv`")
    lines.append("- `alpha_component_budget_v8.csv`")
    lines.append("- `bemv5_base/` or reused BEMv5 folder")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("BEMv8 fixes the two main BEMv7 pathologies: unit-length suppression of the longitudinal scale and independent subtraction of two unstable constants.")
    lines.append("It is still a falsifier. The next gate is convergence of `L_long`, `DeltaF_pair`, and the blind budget under mesh/tube/outer-boundary refinement.")
    lines.append("")
    lines.append(f"Input/source: `{input_source}`")
    (outdir / "blind_alpha_prediction_v8.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v8")
    ap.add_argument("--v5-script", default=None)
    ap.add_argument("--from-bemv5-outdir", default="", help="reuse existing BEMv5 output instead of running BEMv5")

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

    ap.add_argument("--length-samples", type=int, default=12000)
    ap.add_argument("--length-source", choices=["geometric_raw", "spectral_norm", "spectral_norm_rescaled_to_geom_ref"], default="geometric_raw")
    ap.add_argument("--length-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--length-coeff", default="A_M")
    ap.add_argument("--length-fit-min-M", type=int, default=4)
    ap.add_argument("--length-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--pair-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--pair-fit-min-M", type=int, default=4)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--subrun-timeout", type=int, default=300)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.from_bemv5_outdir:
        bemv5_dir = Path(args.from_bemv5_outdir)
        if not bemv5_dir.exists():
            raise FileNotFoundError(bemv5_dir)
        input_source = f"existing BEMv5 outdir={bemv5_dir}"
    else:
        bemv5_dir = outdir / "bemv5_base"
        bemv5_dir.mkdir(parents=True, exist_ok=True)
        v5_script = Path(args.v5_script) if args.v5_script else Path(__file__).with_name("routeB_RT_bem_v5_soft_hk_falsifier.py")
        if not v5_script.exists():
            fallback = Path("/mnt/data/routeB_RT_bem_v5_soft_hk_falsifier.py")
            if fallback.exists():
                v5_script = fallback
            else:
                raise FileNotFoundError(f"BEMv5 script not found: {v5_script}")
        run_bemv5(v5_script, args, bemv5_dir)
        input_source = f"BEMv5 subrun={bemv5_dir}"

    spectra = load_spectra(bemv5_dir)
    manifest = load_manifest(bemv5_dir)
    if not spectra:
        raise RuntimeError(f"No raw_spectrum_*.npy found in {bemv5_dir}")

    result = build_outputs(outdir, spectra, manifest, args)
    write_report(outdir, result, args, input_source)

    config = {"args": vars(args), "input_source": input_source, "bemv5_dir": str(bemv5_dir)}
    (outdir / "run_config_v8.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    b = result["budget"]
    print("=" * 78)
    print("Route B BEMv8 pair-length budget complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"source: {input_source}")
    print(f"target/reference: {result['target']}/{result['reference']}")
    print(f"L_long_target = {b['L_long_target']}")
    print(f"leading length term = {b['leading_length_term_half_NsoftVsoftL']}")
    print(f"DeltaF_pair = {b['DeltaF_pair_target_reference']}")
    print(f"finite correction half = {b['finite_correction_half_pair']}")
    print(f"alpha_inv_pred_blind_v8 = {b['alpha_inv_pred_blind_v8']}")
    print("wrote: geometric_length_audit.csv, hk_length_coefficients_phys.csv, spectral_length_estimate_phys.csv, pair_subtracted_correction.csv, alpha_component_budget_v8.csv, blind_alpha_prediction_v8.md")


if __name__ == "__main__":
    main()
