#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scan recursively for:
    ./**/knot_*.fseries
    ./**/knot_*_ideal.txt

For each file, try to reconstruct one or more oriented closed component curves,
then compute:

- oriented linking matrix L_ij
- per-component writhe Wr_i
- pairwise helicity score
- net chirality/helicity-like score
- pair coherence and self coherence

Supported inputs
----------------
1) .fseries
   Fourier-series centerline format with columns:
       ax bx ay by az bz
   Usually represents one curve. If the file encodes multiple blocks separated
   by blank/comment markers, each block is treated as a component.

2) *_ideal.txt
   Best-effort parser:
   - tries xyz lines
   - splits components on blank lines / comment separators / repeated headers

Outputs
-------
- Console summary
- Optional TSV summary
- Optional JSON details for every file

Usage
-----
python scan_oriented_link_scores_v2.py .
python scan_oriented_link_scores_v2.py . --tsv-out link_scores.tsv --json-out link_scores.json

Optional:
  --n-curve 3000
  --min-points 32
  --gammas 1 1 1
  --only stem_fragment
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import numpy as np


# -----------------------------
# Basic geometry helpers
# -----------------------------
def ensure_closed(curve: np.ndarray) -> np.ndarray:
    if len(curve) < 3:
        return curve
    if np.linalg.norm(curve[0] - curve[-1]) > 1e-12:
        curve = np.vstack([curve, curve[0]])
    return curve


def seg_midpoints_and_vectors(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    p0 = curve[:-1]
    p1 = curve[1:]
    mids = 0.5 * (p0 + p1)
    dls = p1 - p0
    return mids, dls


def gauss_linking_integral(curve_a: np.ndarray, curve_b: np.ndarray) -> float:
    ma, dla = seg_midpoints_and_vectors(curve_a)
    mb, dlb = seg_midpoints_and_vectors(curve_b)

    total = 0.0
    for i in range(len(dla)):
        ra = ma[i]
        dra = dla[i]
        for j in range(len(dlb)):
            rb = mb[j]
            drb = dlb[j]
            r = ra - rb
            nr = np.linalg.norm(r)
            if nr < 1e-15:
                continue
            total += np.dot(np.cross(dra, drb), r) / (nr ** 3)

    return total / (4.0 * math.pi)


def writhe_discrete(curve: np.ndarray) -> float:
    mids, dls = seg_midpoints_and_vectors(curve)
    n = len(dls)
    total = 0.0

    for i in range(n):
        ri = mids[i]
        dli = dls[i]
        for j in range(n):
            if i == j:
                continue
            if abs(i - j) == 1 or abs(i - j) == n - 1:
                continue
            rj = mids[j]
            dlj = dls[j]
            r = ri - rj
            nr = np.linalg.norm(r)
            if nr < 1e-15:
                continue
            total += np.dot(np.cross(dli, dlj), r) / (nr ** 3)

    return total / (4.0 * math.pi)


def oriented_linking_matrix(curves: List[np.ndarray]) -> np.ndarray:
    m = len(curves)
    L = np.zeros((m, m), dtype=float)
    for i in range(m):
        for j in range(i + 1, m):
            lk = gauss_linking_integral(curves[i], curves[j])
            L[i, j] = lk
            L[j, i] = lk
    return L


# -----------------------------
# .fseries parser
# -----------------------------
def parse_fseries_blocks(path: Path, n_curve: int, min_points: int) -> List[np.ndarray]:
    """
    Best-effort parser for one or more Fourier blocks.
    Each block is a set of rows with 6 floats: ax bx ay by az bz.
    Blocks are separated by blank lines or comments that interrupt coeff rows.
    """
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()

    blocks: List[List[List[float]]] = []
    current: List[List[float]] = []

    for raw in text:
        s = raw.strip()
        if not s:
            if current:
                blocks.append(current)
                current = []
            continue
        if s.startswith("%") or s.startswith("#"):
            if current:
                blocks.append(current)
                current = []
            continue

        parts = s.replace(",", " ").split()
        if len(parts) == 6:
            try:
                row = [float(v) for v in parts]
                current.append(row)
                continue
            except ValueError:
                pass

        # break block on anything non-coeff-like
        if current:
            blocks.append(current)
            current = []

    if current:
        blocks.append(current)

    if not blocks:
        raise ValueError(f"{path}: no Fourier coefficient blocks found")

    curves: List[np.ndarray] = []
    theta = np.linspace(0.0, 2.0 * np.pi, n_curve, endpoint=False)

    for block in blocks:
        coeffs = np.asarray(block, dtype=float)
        if coeffs.ndim != 2 or coeffs.shape[1] != 6:
            continue

        xyz = np.zeros((n_curve, 3), dtype=float)
        for idx in range(coeffs.shape[0]):
            j = idx + 1
            ax, bx, ay, by, az, bz = coeffs[idx]
            cj = np.cos(j * theta)
            sj = np.sin(j * theta)
            xyz[:, 0] += ax * cj + bx * sj
            xyz[:, 1] += ay * cj + by * sj
            xyz[:, 2] += az * cj + bz * sj

        xyz -= xyz.mean(axis=0, keepdims=True)
        xyz = ensure_closed(xyz)

        if len(xyz) >= min_points:
            curves.append(xyz)

    return curves


# -----------------------------
# ideal.txt parser
# -----------------------------
_xyz_re = re.compile(
    r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)"
    r"[\s,]+([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)"
    r"[\s,]+([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
)


def parse_ideal_txt_components(path: Path, min_points: int) -> List[np.ndarray]:
    """
    Best-effort parser for knot_*_ideal.txt.
    Splits on blank lines / comment lines / obvious section boundaries.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    components: List[List[List[float]]] = []
    current: List[List[float]] = []

    def flush():
        nonlocal current
        if len(current) >= min_points:
            arr = np.asarray(current, dtype=float)
            arr -= arr.mean(axis=0, keepdims=True)
            arr = ensure_closed(arr)
            components.append(arr.tolist())
        current = []

    for raw in lines:
        s = raw.strip()

        if not s:
            flush()
            continue

        if s.startswith("#") or s.startswith("%") or s.startswith("//"):
            flush()
            continue

        m = _xyz_re.match(s)
        if m:
            current.append([float(m.group(1)), float(m.group(2)), float(m.group(3))])
        else:
            flush()

    flush()

    if not components:
        raise ValueError(f"{path}: no xyz components parsed")

    return [np.asarray(c, dtype=float) for c in components]


# -----------------------------
# Score computation
# -----------------------------
def compute_scores(curves: List[np.ndarray], gammas: Optional[np.ndarray] = None) -> Dict:
    m = len(curves)
    if gammas is None:
        gammas = np.ones(m, dtype=float)
    if len(gammas) != m:
        raise ValueError("gammas length must match number of components")

    L = oriented_linking_matrix(curves)
    Wr = np.array([writhe_discrete(c) for c in curves], dtype=float)

    H_link = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            H_link += gammas[i] * gammas[j] * L[i, j]

    chi_net = float(np.sum((gammas ** 2) * Wr) + 2.0 * H_link)

    abs_pair_sum = 0.0
    signed_pair_sum = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            term = gammas[i] * gammas[j] * L[i, j]
            signed_pair_sum += term
            abs_pair_sum += abs(term)

    pair_coherence = signed_pair_sum / abs_pair_sum if abs_pair_sum > 0 else 0.0

    abs_self_sum = float(np.sum(np.abs((gammas ** 2) * Wr)))
    signed_self_sum = float(np.sum((gammas ** 2) * Wr))
    self_coherence = signed_self_sum / abs_self_sum if abs_self_sum > 0 else 0.0

    return {
        "n_components": m,
        "gammas": gammas.tolist(),
        "linking_matrix": L.tolist(),
        "writhe": Wr.tolist(),
        "H_link": float(H_link),
        "chi_net": float(chi_net),
        "pair_coherence": float(pair_coherence),
        "self_coherence": float(self_coherence),
    }


# -----------------------------
# File dispatch
# -----------------------------
def parse_components(path: Path, n_curve: int, min_points: int) -> List[np.ndarray]:
    suffix = path.suffix.lower()
    if suffix == ".fseries":
        return parse_fseries_blocks(path, n_curve=n_curve, min_points=min_points)
    if path.name.endswith("_ideal.txt"):
        return parse_ideal_txt_components(path, min_points=min_points)
    raise ValueError(f"Unsupported file type: {path}")


# -----------------------------
# Scan
# -----------------------------
def scan_files(root: Path) -> List[Path]:
    found = []
    found.extend(root.rglob("knot_*.fseries"))
    found.extend(root.rglob("knot_*_ideal.txt"))
    # de-duplicate
    found = sorted(set(found))
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Root directory to scan")
    ap.add_argument("--n-curve", type=int, default=3000, help="Samples per Fourier curve")
    ap.add_argument("--min-points", type=int, default=32, help="Minimum points per component")
    ap.add_argument(
        "--gammas",
        nargs="*",
        type=float,
        default=None,
        help="Optional fixed Gamma_i values used for every multi-component file; default all +1",
    )
    ap.add_argument("--only", type=str, default=None, help="Only process files whose path contains this substring")
    ap.add_argument("--tsv-out", type=str, default=None, help="Optional TSV summary output")
    ap.add_argument("--json-out", type=str, default=None, help="Optional full JSON output")
    args = ap.parse_args()

    root = Path(args.root)
    files = scan_files(root)

    if args.only:
        files = [p for p in files if args.only.lower() in str(p).lower()]

    results = []
    print(f"Found {len(files)} candidate files")

    for path in files:
        try:
            curves = parse_components(path, n_curve=args.n_curve, min_points=args.min_points)
            n_components = len(curves)

            gammas = None
            if args.gammas:
                if len(args.gammas) != n_components:
                    # skip custom gammas if mismatch
                    gammas = np.ones(n_components, dtype=float)
                else:
                    gammas = np.asarray(args.gammas, dtype=float)

            scores = compute_scores(curves, gammas=gammas)

            row = {
                "file": str(path),
                "stem": path.stem,
                "n_components": scores["n_components"],
                "H_link": scores["H_link"],
                "chi_net": scores["chi_net"],
                "pair_coherence": scores["pair_coherence"],
                "self_coherence": scores["self_coherence"],
                "writhe": scores["writhe"],
                "linking_matrix": scores["linking_matrix"],
            }
            results.append(row)

            print()
            print(path)
            print(f"  components      : {scores['n_components']}")
            print(f"  H_link          : {scores['H_link']:.6f}")
            print(f"  chi_net         : {scores['chi_net']:.6f}")
            print(f"  pair_coherence  : {scores['pair_coherence']:.6f}")
            print(f"  self_coherence  : {scores['self_coherence']:.6f}")
            print("  linking matrix  :")
            for r in scores["linking_matrix"]:
                print("    " + "  ".join(f"{v: .6f}" for v in r))

        except Exception as e:
            print()
            print(path)
            print(f"  ERROR: {e}")

    # ranking by |pair_coherence|? No: better to sort by positive pair_coherence and |chi_net|
    ranked = sorted(
        results,
        key=lambda r: (
            -float(r["pair_coherence"]),
            -abs(float(r["chi_net"])),
            -abs(float(r["H_link"])),
        ),
    )

    print("\nTop candidates by positive pair coherence")
    print("=========================================")
    for i, r in enumerate(ranked[:20], start=1):
        print(
            f"{i:>3}  {r['stem']:<35}  comps={r['n_components']:>2}  "
            f"pair={r['pair_coherence']:> .6f}  self={r['self_coherence']:> .6f}  "
            f"H={r['H_link']:> .6f}  chi={r['chi_net']:> .6f}"
        )

    if args.tsv_out:
        import csv
        with open(args.tsv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([
                "file", "stem", "n_components",
                "H_link", "chi_net", "pair_coherence", "self_coherence",
                "writhe", "linking_matrix"
            ])
            for r in ranked:
                writer.writerow([
                    r["file"], r["stem"], r["n_components"],
                    r["H_link"], r["chi_net"], r["pair_coherence"], r["self_coherence"],
                    json.dumps(r["writhe"]),
                    json.dumps(r["linking_matrix"]),
                ])
        print(f"\nWrote TSV: {args.tsv_out}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(ranked, indent=2), encoding="utf-8")
        print(f"Wrote JSON: {args.json_out}")


if __name__ == "__main__":
    main()